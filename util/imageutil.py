# Copyright 2020-2024 Peppy Player peppy.player@gmail.com
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
import io

from util.config import *
from PIL import Image, ImageFilter
from PIL.ImageColor import getcolor, getrgb
from PIL.ImageOps import grayscale
from io import BytesIO
from util.fileutil import FOLDER, FOLDER_WITH_ICON, FILE_AUDIO, FILE_PLAYLIST, FILE_IMAGE, FILE_CD_DRIVE
from urllib import request
from urllib.request import urlopen
from mutagen.id3 import ID3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4

FOLDER_ICONS = "icons"
FOLDER_BACKGROUNDS = "backgrounds"
ICON_FOLDER = "folder"
ICON_FILE_AUDIO = "audio-file"
ICON_FILE_PLAYLIST = "playlist"
ICON_CD_DRIVE = "cd-player"
ICON_IMAGE_FILE = "image-file"

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

CATEGORY_ORIGINAL = "original"

HTTP_CONNECTION_TIMEOUT_SEC = 12

class ImageUtil(object):
    """ Image Utility class """
    
    def __init__(self, util):
        """ Initializer.
        
        :param util: utility object
        """
        self.util = util
        self.config = util.config
        self.discogs_util = util.discogs_util

        self.CATEGORY = self.config[ICONS][ICONS_CATEGORY]

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
        self.thumbnail_cache = {}

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

    def get_scale_ratio(self, bounding_box, img, fit_height=False, fit_width=False, fit_all=False):
        """ Return scale ratio calculated from provided constraints (bounding box) and image
        
        :param bounding_box: bounding box
        :param img: image
        :param fit_height: True - fit image height to bounding box
        
        :return: tuple representing scale ratio 
        """
        if not img: return

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
            elif fit_width:
                width = int(width * k1)
                height = int(height * k1)
            elif fit_all:
                width = int(width * (max(k1, k2)))
                height = int(height * (max(k1, k2)))
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

    def scale_image(self, image, ratio):
        """ Scale image using specified ratio
        
        :param image: image to scale
        :param ratio: scaling ratio
              
        :return: scaled image
        """
        if image == None:
            return None
        s = pygame.Surface(ratio, flags=pygame.SRCALPHA)
        if isinstance(image, tuple):
            image = image[1]

        image = self.pre_scale(image)   

        if image:
            d = pygame.image.tostring(image, "RGBA", False)
            img = Image.frombytes("RGBA", image.get_size(), d)
            i = img.resize(ratio)
            d = pygame.image.fromstring(i.tobytes(), i.size, i.mode)
            s.blit(d, (0, 0))
            return s
        else:
            return None

    def pre_scale(self, image):
        """ Scale down very large image to avoid Out of Memory exception in 'pygame.image.tostring'

        :param image: input image

        :return: original input image if pre-scale not reuired, scaled image if pre-scale required
        """
        if image == None: return None

        size = image.get_size()
        large_image_size = 2000
        if size[0] > large_image_size or size[1] > large_image_size:
            k_x = size[0] / large_image_size
            k_y = size[1] / large_image_size
            width = int(size[0] / k_x)
            height = int(size[1] / k_y)
            return pygame.transform.scale(image, (width, height))
        else:
            return image

    def get_image_from_audio_file(self, filename, return_buffer=False):
        """ Fetch image from audio file. 
        Supported formats: MP3, FLAC, MP4, M4A

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

    def get_png_from_surface(self, surface):
        """ Convert Pygame Surface to PNG image

        :param surface: Pygame Surface object

        :return: PNG image
        """
        if surface == None:
            return None

        s = None
        try:
            d = pygame.image.tostring(surface, "RGBA", False)
            img = Image.frombytes("RGBA", surface.get_size(), d)
            buffer = BytesIO()
            img.save(buffer, "PNG")
            s = buffer.getvalue()
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

    def load_svg_icon_main(self, type, filename, color_1, color_2, category, filepath=None):
        """ Load icon with main color

        :param filename: icon filename
        :param bounding_box: icon bounding box
        :param scale: icon scale ratio
        :param filepath: full file path

        :return: icon object
        """
        try:
            if type == MONOCHROME:
                return self.load_svg_icon(filename, color_1, None, 1.0, color_1, category=category, output="svg", filepath=filepath)
            elif type == BI_COLOR:
                return self.load_svg_icon(filename, color_1, None, 1.0, color_2, category=category, output="svg", filepath=filepath)
            elif type == GRADIENT:
                return self.load_svg_icon(filename, color_1, None, 1.0, color_2, True, category=category, output="svg", filepath=filepath)
        except:
            return None

    def load_icon_main(self, filename, bounding_box=None, scale=1.0, filepath=None):
        """ Load icon with main color

        :param filename: icon filename
        :param bounding_box: icon bounding box
        :param scale: icon scale ratio
        :param filepath: full file path

        :return: icon object
        """
        try:
            if self.config[ICONS][ICONS_TYPE] == MONOCHROME:
                return self.load_svg_icon(filename, self.COLOR_MAIN_1, bounding_box, scale, self.COLOR_MAIN_1, filepath=filepath)
            elif self.config[ICONS][ICONS_TYPE] == BI_COLOR:
                return self.load_svg_icon(filename, self.COLOR_MAIN_1, bounding_box, scale, self.COLOR_MAIN_2, filepath=filepath)
            elif self.config[ICONS][ICONS_TYPE] == GRADIENT:
                return self.load_svg_icon(filename, self.COLOR_MAIN_1, bounding_box, scale, self.COLOR_MAIN_2, True, filepath=filepath)
        except:
            return None

    def load_icon_on(self, filename, bounding_box=None, scale=1.0, filepath=None):
        """ Load icon with selection color

        :param filename: icon filename
        :param bounding_box: icon bounding box
        :param scale: icon scale ratio
        :param filepath: full file path

        :return: icon object
        """
        try:
            if self.config[ICONS][ICONS_TYPE] == MONOCHROME:
                return self.load_svg_icon(filename, self.COLOR_ON_1, bounding_box, scale, self.COLOR_ON_1, filepath=filepath)
            elif self.config[ICONS][ICONS_TYPE] == BI_COLOR:
                return self.load_svg_icon(filename, self.COLOR_ON_1, bounding_box, scale, self.COLOR_ON_2, filepath=filepath)
            elif self.config[ICONS][ICONS_TYPE] == GRADIENT:
                return self.load_svg_icon(filename, self.COLOR_ON_1, bounding_box, scale, self.COLOR_ON_2, True, filepath=filepath)
        except:
            None

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

    def load_svg_icon(self, filename, color_1, bounding_box=None, scale=1.0, color_2=None, gradient=False, cache_suffix="", \
        folder=None, filepath=None, category=None, output=None):
        """ Load monochrome SVG image with replaced color
        
        :param filename: svg image file name
        :param color_1: base icon hex color
        :param bounding_box: image bounding box
        :param scale: scale factor
        :param color_2: second hex color
        :param gradient: True - create gradient, False - use solid colors
        :param cache_suffix: cache key suffix
        :param folder: image folder
        :param filepath: full file path
        :param category: icon category (e.g. line, orifinal etc)
        
        :return: bitmap image rasterized from svg image
        """
        if filepath:
            path = filepath
        else:
            filename += EXT_SVG

            if folder != None:
                path = os.path.join(folder, filename)
            else:
                if category == None:
                    path = os.path.join(FOLDER_ICONS, self.CATEGORY, filename)
                else:
                    path = os.path.join(FOLDER_ICONS, category, filename)

        t = path.replace('\\','/')

        if color_2:
            c_2 = "_" + color_2
        else:
            c_2 = ""

        cache_path = t + "_" + str(scale) + "_" + color_1 + c_2 + cache_suffix

        if bounding_box:
            cache_path += str(bounding_box.w) + str(bounding_box.h)
        
        try:
            if output and output == "svg":
                return self.svg_cache[cache_path]

            return (cache_path, self.image_cache[cache_path])
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
            s = self.increment_size(s, "width=\"")
            s = self.increment_size(s, "height=\"")

            bytes = io.BytesIO(s.encode())
            bitmap_image =  pygame.image.load(bytes).convert_alpha()
        except Exception as e:
            logging.debug("Problem parsing SVG file %s %s", path, e)
            return None
        
        if self.config[USAGE][USE_WEB]:
            self.svg_cache[cache_path] = s

        img = self.scale_svg_image(cache_path, bitmap_image, bounding_box, scale)

        if output == "svg":
            return s
        else:
            return img

    def increment_size(self, svg, token):
        """ Increment SVG image size

        :param token: string token deining width or height

        :return: SVG image with incremented by 1 width or height
        """

        start = svg.find(token)

        if start == 0: return None

        end = svg.find("px", start)

        if end == 0: return None

        f = float(svg[start + len(token): end])
        f += 1

        n = svg[0 : start + len(token)] + str(f) + svg[end : ]

        return n

    def load_multi_color_svg_icon(self, filename=None, bounding_box=None, scale=1.0, path=None):
        """ Load SVG image
        
        :param filename: svg image file name
        :param bounding_box: image bounding box
        :param scale: scale factor
        
        :return: bitmap image rasterized from svg image
        """
        if path == None:
            filename += EXT_SVG
            path = os.path.join(FOLDER_ICONS, filename)
        else:
            path = path

        cache_path = path

        if scale != 1.0:
            cache_path += "_" + str(scale)
        
        try:
            i = self.image_cache[cache_path]
            return (cache_path, i)
        except KeyError:
            pass
        
        try:
            s = codecs.open(path, "r").read()
            s = self.increment_size(s, "width=\"")
            s = self.increment_size(s, "height=\"")
            bytes = io.BytesIO(s.encode())
            svg_image =  pygame.image.load(bytes)
        except Exception as e:
            logging.debug("Problem parsing SVG file %s %s", path, e)
            return None

        if self.config[USAGE][USE_WEB]:
            try:
                self.svg_cache[cache_path]
            except KeyError:
                self.svg_cache[cache_path] = codecs.open(path, "r").read()
        
        return self.scale_svg_image(cache_path, svg_image, bounding_box, scale)

    def scale_svg_image(self, cache_path, svg_image, bounding_box=None, scale=1.0):
        """ Scale SVG image
        
        :param cache_path: cache key for image
        :param svg_image: SVG image
        :param bounding_box: image bounding box
        :param scale: scale factor
        
        :return: scaled bitmap image
        """
        w = svg_image.get_size()[0]
        h = svg_image.get_size()[1]
        
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
        
        image = self.scale_image(svg_image, (w_final, h_final))
        self.image_cache[cache_path] = image
        
        return (cache_path, image)

    def get_image_names_from_folder(self, folder):
        """ Get image names from folder
        
        :param folder: image folder
        
        :return: list of image names
        """
        image_names = []        
        for f in os.listdir(folder):
            path = os.path.join(folder, f)
            p = path.lower()
            if p.endswith(EXT_PNG) or p.endswith(EXT_JPG):
                image_names.append(path)     
        return image_names

    def get_scaled_image(self, img):
        width = img[1].get_size()[0]
        height = img[1].get_size()[1]
        w = self.config[SCREEN_INFO][WIDTH]
        h = self.config[SCREEN_INFO][HEIGHT]

        if width == w and height == h:
            return img
        else:
            scale_ratio = self.get_scale_ratio((w, h), img[1], True)
            img_scaled = self.scale_image(img[1], scale_ratio)
            return (img[0], img_scaled)    

    def load_scaled_images(self, folder):
        """ Load all images from folder, scale to fit screen
        
        :param folder: image folder
        
        :return: list of images
        """
        images = []

        for f in os.listdir(folder):
            path = os.path.join(folder, f)
            img = self.load_image(path)
            if img == None: continue
            images.append(self.get_scaled_image(img))
            
        return images

    def load_scaled_image(self, path):
        img = self.load_pygame_image(path, bounding_box=None, use_cache=False)
        if img == None:
            return None
        else:
            return self.get_scaled_image(img)

    def load_images_from_folder(self, folder):
        """ Load all images from folder
        
        :param folder: image folder
        
        :return: list of images
        """
        images = []        
        for f in os.listdir(folder):
            path = os.path.join(folder, f)
            img = self.load_image(path)
            if img:
                images.append(img)     
        return images

    def load_background_images(self, folder):
        """ Load background images
        
        :param folder: images folder 
        """
        image_files = self.load_images_from_folder(folder)
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
        
        :param path: image file path
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
        :param show_label: True - take label into account
        
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
        icon_image_file = self.load_icon_main(ICON_IMAGE_FILE, bb, scale_factor)

        icon_size = self.config[ICON_SIZE]
        if icon_bb:
            w = (icon_bb[0] / 100) * icon_size
            h = (icon_bb[1] / 100) * icon_size
            icon_box = (w, h)
        else:
            icon_box = (icon_size, icon_size)

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
            scaled_img = self.scale_image(icon_folder, ratio)

            folder_name = os.path.basename(os.path.normpath(url))
            if self.config[ALIGN_BUTTON_CONTENT_X] == CENTER and len(folder_name) == 1 and folder_name.isalpha():
                font = self.util.get_font(icon_bb[1])
                scaled_img = font.render(folder_name, 1, self.config[ICONS][ICONS_COLOR_1_MAIN])
                return (GENERATED_IMAGE + folder_name, scaled_img)

            return (icon_folder[0], scaled_img)
        elif file_type == FILE_AUDIO:
            if self.config[ENABLE_EMBEDDED_IMAGES]:
                img = self.get_image_from_audio_file(url)
            else:
                img = None

            if img:
                ratio = self.get_scale_ratio(image_box, img)
                scaled_img = self.scale_image(img, ratio)
                return (url, scaled_img)
            else:
                ratio = self.get_scale_ratio(icon_box, icon_file_audio[1])
                scaled_img = self.scale_image(icon_file_audio, ratio)
                return (icon_file_audio[0], scaled_img)
        elif file_type == FILE_PLAYLIST:
            ratio = self.get_scale_ratio(icon_box, icon_file_playlist[1])
            scaled_img = self.scale_image(icon_file_playlist, ratio)
            return (icon_file_playlist[0], scaled_img)
        elif file_type == FILE_CD_DRIVE:
            return icon_cd_drive
        elif file_type == FOLDER_WITH_ICON:
            img = self.load_image(file_image_path, bounding_box=image_box)
            if img:
                return img
            else:
                return icon_folder
        elif file_type == FILE_IMAGE:
            if file_image_path:
                img = self.load_image(file_image_path, bounding_box=image_box)
                if img:
                    return img
                else:
                    return icon_image_file
            else:
                ratio = self.get_scale_ratio(icon_box, icon_image_file[1])
                scaled_img = self.scale_image(icon_image_file, ratio)
                return (icon_image_file[0], scaled_img)

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

        if img == None:
            return None
        
        if img == None:
            return None

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
            filename = n + EXT_SVG
            path = os.path.join(FOLDER_ICONS, filename)
            image = self.load_multi_color_svg_icon(str(n), bb)
            r = self.get_scale_ratio((bb.w/4, bb.h), image[1], True)
            i = self.scale_image(image, r)
            digits.append((path, i))
            
        return digits

    def get_flipclock_separator(self, height):
        """ Get image for flip clock separator/colon
        
        :param height: image height
        
        :return: separator image
        """
        filename = "colon"
        path = os.path.join(FOLDER_ICONS, filename + EXT_SVG)
        image = self.load_multi_color_svg_icon(filename)
        r = self.get_scale_ratio((height, height), image[1], True)
        i = self.scale_image(image, r)
        return (path, i)

    def get_flipclock_key(self, image_name, height):
        """ Get key image for flip clock 
        
        :param image_name: image name
        :param height: image height
        
        :return: key image
        """
        path = os.path.join(FOLDER_ICONS, image_name + EXT_SVG)
        image = self.load_multi_color_svg_icon(image_name)
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

    def load_image_from_url(self, url):
        """ Load image from specified URL
        
        :param url: image url
        
        :return: image from url
        """
        try:
            hdrs = {'User-Agent': 'PeppyPlayer + https://github.com/project-owner/Peppy'}
            req = request.Request(url, headers=hdrs)
            stream = urlopen(req, timeout=HTTP_CONNECTION_TIMEOUT_SEC).read()

            buf = BytesIO(stream)
            image = pygame.image.load(buf).convert_alpha()
            return (url, image)
        except Exception as e:
            logging.debug(e)
            return None

    def scale_image_with_padding(self, w, h, img, padding=0, scale_factor=1):
        """ Scale image using specified padding and scale factor
        
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

    def get_background_count(self):
        """ Get background count

        :return: the number of available backgrounds
        """
        definitions = self.config[BACKGROUND_DEFINITIONS]
        names = self.config[BACKGROUND][SCREEN_BGR_NAMES]
        if len(names) == 1 and len(names[0]) == 0:
            names = list(definitions.keys())
        return len(names)

    def get_screen_bgr_image(self, index=None, blur_radius=None):
        """ Get screen background image. 
        First check cache, if not in cache load and prepare image and put to cache.

        :param index: image index in the list of definitions
        :param blur_radius: blur radius

        :return: background image tuple - (filename, image) or None if not found
        """
        definitions = self.config[BACKGROUND_DEFINITIONS]
        names = self.config[BACKGROUND][SCREEN_BGR_NAMES]
        if len(names) == 1 and len(names[0]) == 0:
            names = list(definitions.keys())
            del names[0]

        if index != None:
            name = names[index]
        else:
            name = names[random.randrange(0, len(names))]

        info = self.get_bgr_info(name)

        if not info:
            return None

        filename = info[BGR_FILENAME]
        image = None
        cache_key = filename

        if blur_radius:
            cache_key = filename + "." + str(blur_radius)
            info[BLUR_RADIUS] = blur_radius

        try:
            image = self.background_cache[cache_key]
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

        self.background_cache[cache_key] = (filename, i, info["num"])

        return self.background_cache[cache_key]

    def tint_image(self, src):
        """ Tint the provided image 
        The solution was borrowed here:
        https://stackoverflow.com/questions/29332424/changing-colour-of-an-image/29379704#29379704

        :param src: the source image

        :return: the tinted image
        """
        tint_color = "#ffffff"
        tr, tg, tb = getrgb(tint_color)
        tl = getcolor(tint_color, "L")
        if not tl: tl = 1
        tl = float(tl)
        sr, sg, sb = map(lambda tv: tv/tl, (tr, tg, tb))
        luts = (tuple(map(lambda lr: int(lr*sr + 0.5), range(256))) +
                tuple(map(lambda lg: int(lg*sg + 0.5), range(256))) +
                tuple(map(lambda lb: int(lb*sb + 0.5), range(256))))
        l = grayscale(src)
        if Image.getmodebands(src.mode) < 4:
            merge_args = (src.mode, (l, l, l))
        else:
            a = Image.new("L", src.size)
            a.putdata(src.getdata(3))
            merge_args = (src.mode, (l, l, l, a))
            luts += tuple(range(256))

        return Image.merge(*merge_args).point(luts)

    def create_button_images(self, path, bounding_box, bar_height):
        """ Create image button images

        :param path: image path
        :param bounding_box: button bounding box
        :param bar_height: bottom bar height

        :return: tuple with images for On/Off states
        """
        overlay = self.config[COLORS][COLOR_MEDIUM]
        image_off_alpha = 80

        image = self.load_image(path)
        bb_w = bounding_box.w
        bb_h = bounding_box.h
        overlay_height = int((bb_h / 100) * bar_height)

        scale_ratio = self.get_scale_ratio((bb_w, bb_h), image[1], fit_all=True)
        im = self.scale_image(image, scale_ratio)        
        image_on = pygame.Surface((bounding_box.w, bounding_box.h), pygame.SRCALPHA)
        image_on.blit(im, (0, 0), pygame.Rect(0, 0, bb_w, bb_h))
        image_on.fill(overlay, pygame.Rect(0, bb_h - overlay_height, bb_w, overlay_height), pygame.BLEND_RGB_MULT)

        size = image_on.get_size()
        s = pygame.image.tostring(image_on, "RGBA", False)
        image_off = Image.frombytes("RGBA", size, s)
        image_off.putalpha(image_off_alpha)
        tinted = self.tint_image(image_off)
        b = tinted.tobytes("raw", 'RGBA')
        image_off = pygame.image.fromstring(b, size, 'RGBA')
        image_off.fill(overlay, pygame.Rect(0, bb_h - overlay_height, bb_w, overlay_height), pygame.BLEND_RGB_MULT)

        return (image_on, image_off)

    def set_button_images(self, state, bar_height):
        """ Set button images for On/Off states
        
        :param state: button state
        :param bar_height: bottom bar height
        """
        path = os.path.join(state.folder, state.filename + EXT_JPG)
        if not os.path.exists(path):
            path = os.path.join(state.folder, state.filename + EXT_PNG)

        if not os.path.exists(path):
            return

        images = self.create_button_images(path, state.bounding_box, bar_height)
        state.state_off_image = state.icon_base = (GENERATED_IMAGE + state.name + ".off", images[1])
        state.state_on_image = (GENERATED_IMAGE + state.name + ".on", images[0])

    def add_file_icon(self, page, icon_box, icon_box_without_label):
        """ Set file icons

        :param page: page items
        :param icon_box: icon bounding box
        :param icon_box_without_label: icon bounding box without label
        """
        if not page:
            return

        for s in page:
            if getattr(s, "icon_base", None) != None:
                continue 
            has_embedded_image = getattr(s, "has_embedded_image", False)
            if (s.file_type == FOLDER_WITH_ICON or s.file_type == FILE_IMAGE or has_embedded_image) and self.config[HIDE_FOLDER_NAME]:
                s.show_label = False
                w = icon_box_without_label.w
                h = icon_box_without_label.h
            else:
                s.show_label = True
                w = icon_box.w
                h = icon_box.h
            
            s.icon_base = self.get_file_icon(s.file_type, getattr(s, "file_image_path", ""), (w, h), url=s.url, show_label=s.show_label)

            folder_name = os.path.basename(os.path.normpath(s.url))
            if self.config[ALIGN_BUTTON_CONTENT_X] == CENTER and len(folder_name) == 1 and folder_name.isalpha() and self.config[HIDE_FOLDER_NAME]:
                s.show_label = False

    def get_album_art_bgr(self, image):
        """ Get album art background image

        :param image: input image

        :return: background image
        """
        s = {}
        album_art_bgr = self.config[BACKGROUND_DEFINITIONS][USE_ALBUM_ART]
        s[OVERLAY_COLOR] = album_art_bgr[OVERLAY_COLOR]
        s[OVERLAY_OPACITY] = album_art_bgr[OVERLAY_OPACITY]
        s[BLUR_RADIUS] = album_art_bgr[BLUR_RADIUS]

        screen_w = self.config[SCREEN_INFO][WIDTH]
        screen_h = self.config[SCREEN_INFO][HEIGHT]
        image_w = image.get_size()[0]
        image_h = image.get_size()[1]

        k = screen_w / image_w

        scale_ratio = (int(image_w * k), int(image_h * k))
        img = self.scale_image(image, scale_ratio)

        bgr = pygame.Surface((screen_w, screen_h))
        y = (screen_h - img.get_size()[1]) /2

        bgr.blit(img, (0, 0), (0, abs(y), screen_w, screen_h))

        return self.prepare_background(bgr, s)

    def get_thumbnail(self, img_name, k, f, bb):
        """ Get thumbnail image

        :param img_name: image filename
        :param k: scale factor
        :param f: scale ratio
        :param b: bounding box

        :return: thumbname image
        """
        thumbnail = None
        cache_key = img_name + str(k) + str(f)

        if len(img_name) == 0:
            return None

        try:
            thumbnail = self.thumbnail_cache[cache_key]
        except:
            pass

        if thumbnail != None:
            return thumbnail

        image = self.load_image_from_url(img_name)
        if image != None:
            scale_ratio = self.get_scale_ratio((bb.w * f, bb.h * f), image[1], fit_height=True)
            thumbnail = (img_name, self.scale_image(image, scale_ratio))

        self.thumbnail_cache[cache_key] = thumbnail
        return thumbnail
