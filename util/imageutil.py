# Copyright 2020 Peppy Player peppy.player@gmail.com
# 
# This file is part of Peppy Player.
# 
# Peppy Player is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Peppy Player is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Peppy Player. If not, see <http://www.gnu.org/licenses/>.

import os
import pygame
import base64
import logging
import codecs
import random

from util.config import SHOW_EMBEDDED_IMAGES, USAGE, USE_WEB, COLORS, COLOR_BRIGHT, COLOR_CONTRAST, \
    COLOR_DARK_LIGHT, COLOR_MUTE, IMAGE_SIZE, HIDE_FOLDER_NAME, SCREEN_INFO, WIDTH, HEIGHT, \
    BACKGROUND, COLOR, BLUR_RADIUS, OVERLAY_COLOR, OVERLAY_OPACITY, BACKGROUND_DEFINITIONS, BGR_FILENAME, \
    SCREEN_BGR_NAMES, ICONS, ICONS_COLOR_1_MAIN, ICONS_COLOR_1_ON, ICONS_COLOR_2_MAIN, ICONS_COLOR_2_ON, \
    IMAGE_SIZE_WITHOUT_LABEL, ICONS_TYPE, ICON_SIZE
from PIL import Image, ImageFilter
from io import BytesIO
from svg import Parser, Rasterizer
from util.fileutil import FOLDER, FOLDER_WITH_ICON, FILE_AUDIO, FILE_PLAYLIST, FILE_IMAGE, FILE_CD_DRIVE
from urllib import request
from urllib.request import urlopen
from mutagen import File
from mutagen.id3 import ID3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4

FOLDER_ICONS = "icons"
FOLDER_BACKGROUNDS = "backgrounds"
ICON_FOLDER = "folder"
ICON_FILE_AUDIO = "audio-file"
ICON_FILE_PLAYLIST = "playlist"
ICON_CD_DRIVE = "cd-player"

FILE_COLON = "colon.png"
DEFAULT_CD_IMAGE = "cd.png"
SVG_DEFAULT_COLOR_1 = "#808080"
SVG_DEFAULT_COLOR_2 = "#C0C0C0"
SVG_DEFAULT_GRADIENT_COLOR_1 = "#404040"
SVG_DEFAULT_GRADIENT_COLOR_2 = "#A0A0A0"

EXT_PNG = ".png"
EXT_JPG = ".jpg"
EXT_SVG = ".svg"
EXT_MP3 = ".mp3"
EXT_FLAC = ".flac"
EXT_MP4 = ".mp4"
EXT_M4A = ".m4a"

MONOCHROME = "monochrome"
BI_COLOR = "bi-color"
GRADIENT = "gradient"

class ImageUtil(object):
    """ Image Utility class """
    
    def __init__(self, util):
        """ Initializer.
        
        :param util: utility object
        """
        self.util = util
        self.config = util.config
        self.discogs_util = util.discogs_util

        self.COLOR_MAIN_1 = self.color_to_hex(self.config[ICONS][ICONS_COLOR_1_MAIN])
        self.COLOR_ON_1 = self.color_to_hex(self.config[ICONS][ICONS_COLOR_1_ON])

        try:
            self.COLOR_MAIN_2 = self.color_to_hex(self.config[ICONS][ICONS_COLOR_2_MAIN])
            self.COLOR_ON_2 = self.color_to_hex(self.config[ICONS][ICONS_COLOR_2_ON])
        except:
            self.COLOR_MAIN_2 = self.COLOR_ON_2 = "#000000"
            
        self.COLOR_OFF = self.color_to_hex(self.config[COLORS][COLOR_DARK_LIGHT])
        self.COLOR_MUTE = self.color_to_hex(self.config[COLORS][COLOR_MUTE])        

        self.image_cache = {}
        self.image_cache_base64 = {}
        self.svg_cache = {}
        self.background_cache = {}
        self.album_art_url_cache = {}
        self.FILE_EXTENSIONS_EMBEDDED_IMAGES = None
        if self.config[SHOW_EMBEDDED_IMAGES]:
            self.FILE_EXTENSIONS_EMBEDDED_IMAGES = ["." + s for s in self.config[SHOW_EMBEDDED_IMAGES]]

    def load_image(self, path, base64=False, bounding_box=None):
        """ Load and return image
        
        :param path: image path 
        :param base64: True - encode image using base64 algorithm (for web), False - don't encode
        :param bounding_box: bounding box 
        """
        if base64:
            return self.load_base64_image(path)
        else:
            return self.load_pygame_image(path, bounding_box)

    def load_base64_image(self, path, cache_key=None):
        """ Load image and encode it using base64 encoding.

        :param path: image path
        :param cache_key: cache key
        
        :return: base64 encoded image
        """        
        try:
            img = self.image_cache_base64[path]
            return img
        except:
            pass

        key = path
        if cache_key:
            key = cache_key
        
        if EXT_SVG in path:
            svg_image = self.svg_cache[path]
            img = base64.b64encode(svg_image.encode()).decode()
            self.image_cache_base64[key] = img
            return img
        else:
            p = path.lower()
            if p.endswith(EXT_MP3) or p.endswith(EXT_FLAC) or p.endswith(EXT_MP4) or p.endswith(EXT_M4A):
                image_buffer = self.get_image_from_audio_file(path, True)
                if image_buffer:
                    img = base64.b64encode(image_buffer.read()).decode()
                    self.image_cache_base64[key] = img
                    return img

            with open(path, 'rb') as f:
                img = base64.b64encode(f.read()).decode()
                self.image_cache_base64[key] = img
                return img

    def load_pygame_image(self, path, bounding_box=None, use_cache=True):
        """ Load image. 
        First, check if image is in the cache.
        If yes, return the image from the cache.
        If not load image file and place it in the cache.
        
        :param path: image path
        :param bounding_box: bounding box
        :param use_cache: True - use cache, False - don't use cache
        
        :return: tuple where the first element is the path to the image and the second element is the image itself
        """
        image = None

        if use_cache:
            try:
                p = path
                if bounding_box:
                    p = path + str(bounding_box[0])
                i = self.image_cache[p]
                return (path, i)
            except KeyError:
                pass
            
        try:            
            image = pygame.image.load(path.encode("utf-8")).convert_alpha()            
        except Exception:
            pass
            
        if image:
            img = image
            p = path
            if bounding_box:
                scale_ratio = self.get_scale_ratio(bounding_box, img)
                img = self.scale_image(image, scale_ratio)
                p = path + str(bounding_box[0])
            if use_cache:
                self.image_cache[p] = img
            return (path, img)
        else:
            return None

    def get_scale_ratio(self, bounding_box, img, fit_height=False):
        """ Return scale ratio calculated from provided constraints (bounding box) and image
        
        :param bounding_box: bounding box
        :param img: image
        :param fit_height: True - fit image height to bounding box
        
        :return: tuple representing scale ratio 
        """
        w = bounding_box[0]
        h = bounding_box[1]
        width = img.get_size()[0]
        height = img.get_size()[1]
        
        if (width >= w and height > h) or (width > w and height >= h):
            k1 = w/width
            k2 = h/height                                
            if fit_height:
                width = int(width * k2)
                height = int(height * k2)
            else:
                width = int(width * (min(k1, k2)))
                height = int(height * (min(k1, k2)))
        elif width > w and height < h:
            k = w/width
            width = int(width * k)
            height = int(height * k)
        elif width < w and height > h:
            k = h/height
            width = int(width * k)
            height = int(height * k)
        elif width < w and height < h:
            k1 = w/width
            k2 = h/height                                
            width = int(width * (min(k1, k2)))
            height = int(height * (min(k1, k2)))
        return (width, height)        

    def scale_image(self, image, ratio, argb=False):
        """ Scale image using specified ratio
        
        :param image: image to scale
        :param ratio: scaling ratio
        :param argb: True - ARGB order, False - RGBA order
              
        :return: scaled image
        """
        if image == None:
            return None
        s = pygame.Surface(ratio, flags=pygame.SRCALPHA)
        if isinstance(image, tuple):
            image = image[1]
        if image:
            d = pygame.image.tostring(image, "RGBA", False)
            img = Image.frombytes("RGBA", image.get_size(), d)
            i = img.resize(ratio)
            d = pygame.image.fromstring(i.tobytes(), i.size, i.mode)
            s.blit(d, (0, 0))

            if argb:
                r, g, b, a = s.get_shifts()
                rm, gm, bm, am = s.get_masks()
                s.set_shifts((b, g, r, a))
                s.set_masks((bm, gm, rm, am))
            return s
        else:
            return None

    def get_image_from_audio_file(self, filename, return_buffer=False):
        """ Fetch image from audio file. Only MP3 and FLAC supported

        :param filename: file name
        :param return_buffer: True - return image buffer, False - return Pygame image
        :return: image or None if not found
        """
        if not filename: return None

        name = filename.lower()

        if name.endswith(EXT_MP3):
            if self.FILE_EXTENSIONS_EMBEDDED_IMAGES and EXT_MP3 in self.FILE_EXTENSIONS_EMBEDDED_IMAGES:
                return self.get_image_from_mp3(filename, return_buffer)
        elif name.endswith(EXT_FLAC):
            if self.FILE_EXTENSIONS_EMBEDDED_IMAGES and EXT_FLAC in self.FILE_EXTENSIONS_EMBEDDED_IMAGES:
                return self.get_image_from_flac(filename, return_buffer)
        elif name.endswith(EXT_MP4) or name.endswith(EXT_M4A):
            if self.FILE_EXTENSIONS_EMBEDDED_IMAGES and ((EXT_MP4 in self.FILE_EXTENSIONS_EMBEDDED_IMAGES) or (EXT_M4A in self.FILE_EXTENSIONS_EMBEDDED_IMAGES)):
                return self.get_image_from_mp4(filename, return_buffer)

        return None

    def get_image_from_mp3(self, filename, return_buffer=False):
        """ Fetch image from mp3 file

        :param filename: file name
        :param return_buffer: True - return image buffer, False - return Pygame image
        :return: image or None if not found
        """
        try:
            tags = ID3(filename)
        except:
            return None

        if tags and tags.get("APIC:"):
            try:
                data = tags.get("APIC:").data
                buffer = BytesIO(data)
                if return_buffer:
                    return buffer
                else:
                    return pygame.image.load(buffer).convert_alpha()
            except:
                return None
        else:
            return None

    def get_image_from_flac(self, filename, return_buffer=False):
        """ Fetch image from flac file

        :param filename: file name
        :param return_buffer: True - return image buffer, False - return Pygame image
        :return: image or None if not found
        """
        try:
            pictures = FLAC(filename).pictures
            if pictures:
                data = pictures[0].data
                buffer = BytesIO(data)
                if return_buffer:
                    return buffer
                else:
                    return pygame.image.load(buffer).convert_alpha()
            else:
                return None
        except:
            return None

    def get_image_from_mp4(self, filename, return_buffer=False):
        """ Fetch image from mp4/m4a file

        :param filename: file name
        :param return_buffer: True - return image buffer, False - return Pygame image
        :return: image or None if not found
        """
        try:
            f = MP4(filename)
            t = f.tags
            pictures = t['covr']
            if pictures:
                data = pictures[0]
                buffer = BytesIO(data)
                if return_buffer:
                    return buffer
                else:
                    return pygame.image.load(buffer).convert_alpha()
            else:
                return None
        except:
            return None

    def get_audio_file_icon(self, folder, bb, url=None):
        """ Return audio file icon which is album art image. 
        If it's not available then CD image will be returned.
        
        :param folder: folder name 
        :param bb: bounding box  
        :param url: audio file name

        :return: audio file icon
        """
        if url:
            img = self.get_image_from_audio_file(url)
            if img:
                ratio = self.get_scale_ratio((bb.w, bb.h), img)
                scaled_img = self.scale_image(img, ratio)
                return (url, scaled_img)

        d = os.path.join(FOLDER_ICONS, DEFAULT_CD_IMAGE)
        p = self.util.get_folder_image_path(folder)
        if not p: p = d
        img = self.load_image(p, False, (bb.w, bb.h))

        return (p, img[1])

    def get_base64_surface(self, surface):
        """ Encode Pygame Surface using Base 64

        :param surface: Pygame Surface object

        :return: base 64 encoded surface as PNG image
        """
        if surface == None:
            return None
        
        s = None
        try:
            d = pygame.image.tostring(surface, "RGBA", False)
            img = Image.frombytes("RGBA", surface.get_size(), d)
            buffer = BytesIO()
            img.save(buffer, "PNG")
            s = base64.b64encode(buffer.getvalue()).decode()
        except Exception as e:
            logging.debug(e)

        return s

    def blur_image(self, surface, blur_radius, argb=False):
        """ Blur image using Gaussian method

        :param surface: surface to blur
        :param blur_radius: integer number defining how blurry the surface should be
        :param argb: True - ARGB order, False - RGBA order

        :return: blurred surface
        """
        size = surface.get_size()

        if argb:
            r, g, b, a = surface.get_shifts()
            rm, gm, bm, am = surface.get_masks()
            surface.set_shifts((b, g, r, a))
            surface.set_masks((bm, gm, rm, am))

        s = pygame.image.tostring(surface, "RGBA", False)
        img = Image.frombytes("RGBA", size, s)
        
        blurred = img.filter(ImageFilter.GaussianBlur(blur_radius))
        b = blurred.tobytes("raw", 'RGBA')

        return pygame.image.fromstring(b, size, 'RGBA')

    def invert_image(self, surface):
        """ Invert colors of the Pygame surface

        :param surface: image to invert

        :return: inverted image
        """
        size = surface.get_size()
        img = pygame.Surface(size, pygame.SRCALPHA)
        img.fill((255, 255, 255, 255))
        img.blit(surface, (0, 0), None, pygame.BLEND_RGB_SUB)

        return img

    def load_icon_main(self, filename, bounding_box=None, scale=1.0):
        """ Load icon with main color

        :param filename: icon filename
        :param bounding_box: icon bounding box
        :param scale: icon scale ratio

        :return: icon object
        """
        if self.config[ICONS][ICONS_TYPE] == MONOCHROME:
            return self.load_svg_icon(filename, self.COLOR_MAIN_1, bounding_box, scale, self.COLOR_MAIN_1)
        elif self.config[ICONS][ICONS_TYPE] == BI_COLOR:
            return self.load_svg_icon(filename, self.COLOR_MAIN_1, bounding_box, scale, self.COLOR_MAIN_2)
        elif self.config[ICONS][ICONS_TYPE] == GRADIENT:
            return self.load_svg_icon(filename, self.COLOR_MAIN_1, bounding_box, scale, self.COLOR_MAIN_2, True)

    def load_icon_on(self, filename, bounding_box=None, scale=1.0):
        """ Load icon with selection color

        :param filename: icon filename
        :param bounding_box: icon bounding box
        :param scale: icon scale ratio

        :return: icon object
        """
        if self.config[ICONS][ICONS_TYPE] == MONOCHROME:
            return self.load_svg_icon(filename, self.COLOR_ON_1, bounding_box, scale, self.COLOR_ON_1)
        elif self.config[ICONS][ICONS_TYPE] == BI_COLOR:
            return self.load_svg_icon(filename, self.COLOR_ON_1, bounding_box, scale, self.COLOR_ON_2)
        elif self.config[ICONS][ICONS_TYPE] == GRADIENT:
            return self.load_svg_icon(filename, self.COLOR_ON_1, bounding_box, scale, self.COLOR_ON_2, True)

    def load_icon_off(self, filename, bounding_box=None, scale=1.0):
        """ Load icon with disabled color

        :param filename: icon filename
        :param bounding_box: icon bounding box
        :param scale: icon scale ratio

        :return: icon object
        """
        return self.load_svg_icon(filename, self.COLOR_OFF, bounding_box, scale, self.COLOR_OFF)

    def load_icon_mute(self, filename, bounding_box=None, scale=1.0):
        """ Load icon with mute color

        :param filename: icon filename
        :param bounding_box: icon bounding box
        :param scale: icon scale ratio

        :return: icon object
        """
        return self.load_svg_icon(filename, self.COLOR_MUTE, bounding_box, scale, self.COLOR_MUTE)

    def load_svg_icon(self, filename, color_1, bounding_box=None, scale=1.0, color_2=None, gradient=False):
        """ Load monochrome SVG image with replaced color
        
        :param filename: svg image file name
        :param color_1: base icon hex color
        :param bounding_box: image bounding box
        :param scale: scale factor
        
        :return: bitmap image rasterized from svg image
        """ 
        filename += EXT_SVG
        path = os.path.join(FOLDER_ICONS, filename)
        t = path.replace('\\','/')
        if color_2:
            c_2 = "_" + color_2
        else:
            c_2 = ""
        cache_path = t + "_" + str(scale) + "_" + color_1 + c_2
        
        try:
            i = self.image_cache[cache_path]
            return (cache_path, i)
        except KeyError:
            pass
        
        s = codecs.open(path, "r").read()

        if gradient:
            g = "url(#gradient)"
            s = s.replace(SVG_DEFAULT_GRADIENT_COLOR_1, color_2)
            s = s.replace(SVG_DEFAULT_GRADIENT_COLOR_2, color_1)
            s = s.replace(SVG_DEFAULT_COLOR_1, g)
            s = s.replace(SVG_DEFAULT_COLOR_2, g)
        else:
            if color_2:
                s = s.replace(SVG_DEFAULT_COLOR_2, color_1)
                s = s.replace(SVG_DEFAULT_COLOR_1, color_2)
            else:
                s = s.replace(SVG_DEFAULT_COLOR_1, color_1)
        
        try:
            bitmap_image = Parser.parse(s)
        except:
            logging.debug("Problem parsing file %s", path)
            return None
        
        if self.config[USAGE][USE_WEB]:
            self.svg_cache[cache_path] = s
        
        return self.scale_svg_image(cache_path, bitmap_image, bounding_box, scale)
    
    def load_multi_color_svg_icon(self, filename, bounding_box=None, scale=1.0):
        """ Load SVG image
        
        :param filename: svg image file name
        :param bounding_box: image bounding box
        :param scale: scale factor
        
        :return: bitmap image rasterized from svg image
        """        
        filename += EXT_SVG
        path = os.path.join(FOLDER_ICONS, filename)
        cache_path = path + "_" + str(scale)
        
        try:
            i = self.image_cache[cache_path]
            return (cache_path, i)
        except KeyError:
            pass
        
        try:
            svg_image = Parser.parse_file(path)
        except:
            logging.debug("Problem parsing file %s", path)
            return None

        if self.config[USAGE][USE_WEB]:
            try:
                self.svg_cache[cache_path]
            except KeyError:
                t = cache_path.replace('\\','/')
                self.svg_cache[t] = codecs.open(path, "r").read()
        
        return self.scale_svg_image(cache_path, svg_image, bounding_box, scale)

    def scale_svg_image(self, cache_path, svg_image, bounding_box=None, scale=1.0):
        """ Scale SVG image
        
        :param cache_path: cache key for image
        :param svg_image: SVG image
        :param bounding_box: image bounding box
        :param scale: scale factor
        
        :return: scaled bitmap image
        """
        w = svg_image.width + 2
        h = svg_image.height + 2
        
        if bounding_box == None:
            bb_w = w * scale
            bb_h = h * scale
        else:
            bb_w = bounding_box.w * scale
            bb_h = bounding_box.h * scale
            
        w_scaled = bb_w / w
        h_scaled = bb_h / h
        scale_factor = min(w_scaled, h_scaled)
        w_final = int(w * scale_factor)
        h_final = int(h * scale_factor)
        
        r = Rasterizer()        
        buff = r.rasterize(svg_image, w_final, h_final, scale_factor)    
        image = pygame.image.frombuffer(buff, (w_final, h_final), 'RGBA')
        
        self.image_cache[cache_path] = image
        
        return (cache_path, image)

    def load_screensaver_images(self, folder):
        """ Load screensaver images (e.g. for Slideshow plug-in)
        
        :param folder: new image folder
        
        :return: list of images
        """
        slides = []        
        for f in os.listdir(folder):
            path = os.path.join(folder, f)
            img = self.load_image(path)
            if img:
                slides.append(img)     
        return slides

    def load_background_images(self, folder):
        """ Load background images
        
        :param folder: images folder 
        """
        image_files = self.load_screensaver_images(folder)
        w = self.config[SCREEN_INFO][WIDTH]
        h = self.config[SCREEN_INFO][HEIGHT]
        images = []
        for image in image_files:
            width = image[1].get_size()[0]
            height = image[1].get_size()[1]
            
            if width == w and height == h:
                images.append(image)
            else:
                scale_ratio = self.get_scale_ratio((w, h), image[1], True)
                img = self.scale_image(image[1], scale_ratio)
                t = (image[0], img)
                images.append(t)
        
        return images

    def prepare_flag_image(self, path, button_bounding_box):
        """ Prepare flag image
        
        :param button_bounding_box: button bounding box
        
        :return: flag image
        """      
        flag = self.load_image(path)
        bb_w = button_bounding_box.w
        bb_h = button_bounding_box.h
        scale_ratio = self.get_scale_ratio((bb_w, bb_h), flag[1])
        im = self.scale_image(flag, (scale_ratio[0], scale_ratio[1]))        
        img = pygame.Surface((scale_ratio[0], scale_ratio[1]), pygame.SRCALPHA)
        img.blit(im, (0, 0))
 
        return img

    def get_file_icon(self, file_type, file_image_path=None, icon_bb=None, scale_factor=0.6, url=None, show_label=True):
        """ Load image representing file. Six types of icons supported:
        1. Folder icon
        2. Audio file icon
        3. Image fetched from audio file
        4. Folder with folder icon (folder icon will be displayed in this case)
        5. Playlist icon
        6. CD Drive
        
        :param file_type: defines file type 
        :param file_image_path: path to image file       
        :param icon_bb: image bounding box
        :param scale_factor: scale factor
        :param url: file name
        
        :return: image representing file
        """
        if icon_bb:
            bb = pygame.Rect(0, 0, icon_bb[0], icon_bb[1])
        else:
            bb = None
        
        icon_folder = self.load_icon_main(ICON_FOLDER, bb, scale_factor)
        icon_file_audio = self.load_icon_main(ICON_FILE_AUDIO, bb, scale_factor)
        icon_file_playlist = self.load_icon_main(ICON_FILE_PLAYLIST, bb, scale_factor)
        icon_cd_drive = self.load_icon_main(ICON_CD_DRIVE, bb, scale_factor)

        icon_size = self.config[ICON_SIZE]
        w = (icon_bb[0] / 100) * icon_size
        h = (icon_bb[1] / 100) * icon_size
        icon_box = (w, h)

        image_size = self.config[IMAGE_SIZE]
        if icon_bb:
            if show_label:
                image_box = ((icon_bb[0] /100) * image_size, (icon_bb[1] / 100) * image_size)
            else:
                w = (icon_bb[0] / 100) * self.config[IMAGE_SIZE_WITHOUT_LABEL]
                h = (icon_bb[1] / 100) * self.config[IMAGE_SIZE_WITHOUT_LABEL]
                image_box = (w, h)

        if file_type == FOLDER:
            ratio = self.get_scale_ratio(icon_box, icon_folder[1])
            scaled_img = self.scale_image(icon_folder, ratio, True)
            return (icon_folder[0], scaled_img)
        elif file_type == FILE_AUDIO:
            img = self.get_image_from_audio_file(url)
            if img:
                ratio = self.get_scale_ratio(image_box, img)
                scaled_img = self.scale_image(img, ratio)
                return (url, scaled_img)
            else:
                ratio = self.get_scale_ratio(icon_box, icon_file_audio[1])
                scaled_img = self.scale_image(icon_file_audio, ratio, True)
                return (icon_file_audio[0], scaled_img)
        elif file_type == FILE_PLAYLIST:
            ratio = self.get_scale_ratio(icon_box, icon_file_playlist[1])
            scaled_img = self.scale_image(icon_file_playlist, ratio, True)
            return (icon_file_playlist[0], scaled_img)
        elif file_type == FILE_CD_DRIVE:
            return icon_cd_drive
        elif file_type == FOLDER_WITH_ICON or file_type == FILE_IMAGE:
            img = self.load_image(file_image_path, bounding_box=image_box)
            if img:
                return img
            else:
                return icon_folder        

    def get_cd_album_art(self, album, bb):
        """ Return album art image
        
        :param album: artist name, song name
        :param bb: bounding box 
        
        :return: album art image
        """
        img = url = None
        
        if album != None:
            try:
                url = self.album_art_url_cache[album]
            except:
                url = self.discogs_util.get_album_art_url(album)
                if url != None:
                    self.album_art_url_cache[album] = url
        
        if url == None:
            d = os.path.join(FOLDER_ICONS, DEFAULT_CD_IMAGE)
            img = self.load_image(d)
            url = d
        else:
            try:
                i = self.image_cache[url]
                return (url, i)
            except KeyError:
                pass
            img = self.load_image_from_url(url)
        
        ratio = self.get_scale_ratio((bb.w, bb.h), img[1])
        if ratio[0] % 2 != 0:
            ratio = (ratio[0] - 1, ratio[1])
        if ratio[1] % 2 != 0:
            ratio = (ratio[0], ratio[1] - 1)   
        img = self.scale_image(img, ratio)
        
        if url != None:
            self.image_cache[url] = img
        
        return (url, img)

    def get_flipclock_digits(self, bb):
        """ Get digits for the flip clock
        
        :param bb: digit image bounding box
        
        :return: list of digit images
        """
        digits = []
        
        for n in map(str, range(10)):
            filename = n + EXT_PNG
            path = os.path.join(FOLDER_ICONS, filename)
            t = path.replace('\\','/')
            image = self.load_image(t)
            r = self.get_scale_ratio((bb.w/4, bb.h), image[1], True)
            i = self.scale_image(image, r)
            digits.append((path, i))
            
        return digits

    def get_flipclock_separator(self, height):
        """ Get image for flip clock separator/colon
        
        :param height: image height
        
        :return: separator image
        """
        path = os.path.join(FOLDER_ICONS, FILE_COLON)
        t = path.replace('\\','/')
        image = self.load_image(t)
        r = self.get_scale_ratio((height, height), image[1], True)
        i = self.scale_image(image, r)
        return (path, i)

    def get_flipclock_key(self, image_name, height):
        """ Get key image for flip clock 
        
        :param image_name: image name
        :param height: image height
        
        :return: key image
        """
        path = os.path.join(FOLDER_ICONS, image_name)
        t = path.replace('\\','/')
        image = self.load_image(t)
        s = image[1].get_size()
        h = height / 7.05
        k = h / s[1]
        w = s[0] * k
        r = self.get_scale_ratio((w, h), image[1], True)
        i = self.scale_image(image, r)
        return (path, i)

    def color_to_hex(self, color):
        """ Convert color tuple into hex representation for web
        
        :param color: list of integer numbers
        
        :return: hex representation of the color
        """
        if not color:
            return None

        if len(color) == 4:
            return "#%08x" % ((color[0] << 24) + (color[1] << 16) + (color[2] << 8) + color[3])
        else:
            return "#%06x" % ((color[0] << 16) + (color[1] << 8) + color[2])

    def load_image_from_url(self, url, header=False):
        """ Load image from specified URL
        
        :param url: image url
        
        :return: image from url
        """
        try:
            if header == False:
                stream = urlopen(url).read()
            else:
                hdrs = {'User-Agent': 'PeppyPlayer +https://github.com/project-owner/Peppy'}
                req = request.Request(url, headers=hdrs)
                stream = urlopen(req).read()

            buf = BytesIO(stream)
            image = pygame.image.load(buf).convert_alpha()
            return (url, image)
        except Exception as e:
            logging.debug(e)
            return None

    def scale_image_with_padding(self, w, h, img, padding=0, scale_factor=1):
        """ Scale image using specified padding and sacle factor
        
        :param w: image width
        :param h: image height
        :param img: image
        :param padding: padding
        :param scale_factor: scale factor  
               
        :return: scaled image
        """
        w_adjusted = (w - (padding * 2)) * scale_factor
        h_adjusted = (h - (padding * 2)) * scale_factor 
        scale_ratio = self.get_scale_ratio((w_adjusted, h_adjusted), img)
        return self.scale_image(img, scale_ratio)

    def load_menu_screen_image(self, url, w, h):
        """ Load image
        
        :param url: image url
        :param w: image width
        :param h: image height
        
        :return: hash of the input string
        """
        img_scaled = None
        img = self.load_image_from_url(url)
        image_padding = 4 
        if img:
            img_scaled = self.scale_image_with_padding(w, h, img[1], image_padding, 1.0)                
        
        if not img_scaled:
            return None
        else:
            return img_scaled

    def get_bgr_info(self, name):
        """ Get background definition by name

        :param name: definition section name

        :return: definition section
        """
        definitions = self.config[BACKGROUND_DEFINITIONS]
        names = self.config[BACKGROUND][SCREEN_BGR_NAMES]
        if len(names) == 1 and len(names[0]) == 0:
            names = list(definitions.keys())
        
        for n in names:
            if n not in definitions.keys():
                continue

            section = definitions[n]
            if n == name:
                section["num"] = n
                return section

        return None

    def prepare_background(self, surface, section):
        """
        Paint surface by specified color.

        :param surface: surface to paint
        :param section: background definition

        :return: new painted surface
        """
        image = surface
        size = surface.get_size()
        result = pygame.Surface(size)
        result.fill((0, 0, 0), None, pygame.BLEND_RGB_ADD)
        overlay = section[OVERLAY_COLOR]
        overlay_opacity = section[OVERLAY_OPACITY]
        blur_radius = section[BLUR_RADIUS]

        if blur_radius and blur_radius > 0:
            image = self.blur_image(image, blur_radius)

        if overlay:
            image.fill(overlay, None, pygame.BLEND_RGBA_ADD)
            image.fill((255, 255, 255, overlay_opacity), None, pygame.BLEND_RGBA_MULT)

        result.blit(image, (0, 0))

        return result

    def get_screen_bgr_image(self):
        """ Get screen background image. 
        First check cache, if not in cache load and prepare image and put to cache.

        :return: background image tuple - (filename, image) or None if not found
        """
        definitions = self.config[BACKGROUND_DEFINITIONS]
        names = self.config[BACKGROUND][SCREEN_BGR_NAMES]
        if len(names) == 1 and len(names[0]) == 0:
            names = list(definitions.keys())

        name = names[random.randrange(0, len(names))]
        info = self.get_bgr_info(name)

        if not info:
            return None

        filename = info[BGR_FILENAME]
        image = None

        try:
            image = self.background_cache[filename]
            return image
        except:
            pass

        path = os.path.join(FOLDER_BACKGROUNDS, filename)
        image = self.load_pygame_image(path, None, use_cache=False)

        if not image:
            return None

        w = self.config[SCREEN_INFO][WIDTH]
        h = self.config[SCREEN_INFO][HEIGHT]
        width = image[1].get_size()[0]
        height = image[1].get_size()[1]
                
        if width == w and height == h:
            i = self.prepare_background(image, info)            
        else:
            ratio = min(width / w, height / h)
            scale_ratio = (int(width / ratio), int(height / ratio))
            img = self.scale_image(image[1], scale_ratio)
            i = self.prepare_background(img, info)

        self.background_cache[filename] = (filename, i, info["num"])

        return self.background_cache[filename]    
