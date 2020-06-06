# Copyright 2016-2017 Peppy Player peppy.player@gmail.com
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

AUDIOKNIGI_ROWS = 2
AUDIOKNIGI_COLUMNS = 6
AUDIOKNIGI_PAGE_SIZE = AUDIOKNIGI_ROWS * AUDIOKNIGI_COLUMNS

BASE_URL = "https://akniga.org/index/"
SECTION_URL = "https://akniga.org/section/"
BOOK_URL = "https://akniga.org/ajax/b/"
PREVIEW_URL = "https://akniga.org/uploads/media/topic/"
AUTHOR_URL_PREFIX = "https://akniga.org/author/"
AUTHOR_URL = "https://akniga.org/authors/?prefix="
PAGE_URL_PREFIX = "/page"
INITIAL_CHAR = "А"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0"
COOKIE = 'PHPSESSID=684aenmfot5n5tqorri6e65q4s'
HASH = '{"ct":"fvd6UIlT55XufSSowjmM1E6H4SuJza8oCY3K+1MEzUxZ4JeFXiM4KiagcJDHfFWD","iv":"ae21433aac8e8ecdf7ed1e2f6c30c49e","s":"601b7db096cf507c"}'
SEC_KEY = "4329ea301927d43b592e9705bf4c95cb"
AITEMS = "aItems"

ABC_RU = ["А", "Б", "В", "Г", "Д", "Е", "Ё", "Ж", "З", "И", "Й", "К", "Л", "М", "Н", "О", "П", "Р", "С", "Т",
               "У", "Ф", "Х", "Ц", "Ч", "Ш", "Щ", "Э", "Ю", "Я"]
FILTERS_RU = dict()
FILTERS_RU["А"] = ["Аб", "Ав", "Аг", "Ад", "Аж", "Аз", "Ай", "Ак", "Ал", "Ам", "Ан", "Ап", "Ар",
                        "Ас", "Ат", "Ау", "Аф", "Ах", "Аш"]
FILTERS_RU["Б"] = ["Ба", "Бе", "Бж", "Би", "Бл", "Бо", "Бр", "Бу", "Бы", "Бь", "Бэ", "Бю", "Бя", "Бё"]
FILTERS_RU["В"] = ["Ва", "Вв", "Ве", "Ви", "Вл", "Вн", "Во", "Вр", "Ву", "Вы", "Вэ", "Вя"]
FILTERS_RU["Г"] = ["Га", "Гв", "Гд", "Ге", "Ги", "Гл", "Гн", "Го", "Гр", "Гу", "Гх", "Гь", "Гэ", "Гю",
                        "Гё"]
FILTERS_RU["Д"] = ["Д'", "Да", "Дв", "Де", "Дж", "Дз", "Ди", "Дм", "Дн", "До", "Др", "Ду", "Ды", "Дь",
                        "Дэ", "Дю", "Дя", "Дё"]
FILTERS_RU["Е"] = ["Ев", "Ег", "Еж", "Ез", "Ек", "Ел", "Ем", "Ен", "Ер", "Ес", "Ет", "Еф", "Еш"]
FILTERS_RU["Ж"] = ["Жа", "Жв", "Жд", "Же", "Жи", "Жо", "Жу"]
FILTERS_RU["З"] = ["За", "Зв", "Зг", "Зд", "Зе", "Зи", "Зл", "Зн", "Зо", "Зу", "Зы", "Зю"]
FILTERS_RU["И"] = ["Иа", "Иб", "Ив", "Иг", "Ид", "Из", "Ик", "Ил", "Им", "Ин", "Ио", "Ип", "Ир",
                        "Ис", "Иш"]
FILTERS_RU["К"] = ["Ка", "Кв", "Ке", "Ки", "Кл", "Кн", "Ко", "Кр", "Ку", "Кх", "Кш", "Кь", "Кэ", "Кю",
                        "Кё"]
FILTERS_RU["Л"] = ["Ла", "Ле", "Ли", "Лл", "Ло", "Лу", "Лы", "Ль", "Лэ", "Лю", "Ля", "Лё"]
FILTERS_RU["М"] = ["Ма", "Ме", "Ми", "Мл", "Мн", "Мо", "Му", "Мы", "Мь", "Мэ", "Мю", "Мя", "Мё"]
FILTERS_RU["Н"] = ["На", "Не", "Ни", "Но", "Ну", "Нь", "Нэ", "Ню"]
FILTERS_RU["О"] = ["Оа", "Об", "Ов", "Ог", "Од", "Оз", "Ок", "Ол", "Ом", "Он", "Оп", "Ор",
                        "Ос", "От", "Оу", "Оф", "Ох", "Оэ"]
FILTERS_RU["П"] = ["Па", "Пе", "Пи", "Пл", "По", "Пр", "Пт", "Пу", "Пф", "Пч", "Пш", "Пы", "Пь", "Пэ"]
FILTERS_RU["Р"] = ["Ра", "Ре", "Рж", "Ри", "Ро", "Ру", "Ры", "Рэ", "Рю", "Ря"]
FILTERS_RU["С"] = ["С.", "Са", "Св", "Сг", "Се", "Си", "Ск", "Сл", "См", "Сн", "Со", "Сп", "Ср", "Ст",
                        "Су", "Сы", "Сь", "Сэ", "Сю", "Сё"]
FILTERS_RU["Т"] = ["Та", "Тв", "Те", "Ти", "Тк", "То", "Тр", "Ту", "Тх", "Ты", "Тэ", "Тю", "Тя", "Тё"]
FILTERS_RU["У"] = ["Уа", "Ув", "Уг", "Уд", "Уи", "Ук", "Ул", "Ум", "Ун", "Уо", "Ур", "Ус", "Ут",
                        "Ух", "Уш", "Уэ"]
FILTERS_RU["Ф"] = ["Фа", "Фе", "Фи", "Фл", "Фо", "Фр", "Фу", "Фф", "Фь", "Фэ", "Фю", "Фё"]
FILTERS_RU["Х"] = ["Ха", "Хв", "Хе", "Хи", "Хл", "Хм", "Хо", "Хр", "Ху", "Хь", "Хэ", "Хю", "Хё"]
FILTERS_RU["Ц"] = ["Ца", "Цв", "Це", "Ци", "Цо", "Цу", "Цы"]
FILTERS_RU["Ч"] = ["Ча", "Чб", "Че", "Чж", "Чи", "Чо", "Чу", "Чх", "Чё"]
FILTERS_RU["Ш"] = ["Ша", "Шв", "Ше", "Ши", "Шк", "Шл", "Шм", "Шн", "Шо", "Шп", "Шр", "Шт", "Шу", "Шю",
                        "Шё"]
FILTERS_RU["Щ"] = ["Ще", "Щу", "Щё"]
FILTERS_RU["Э"] = ["Эб", "Эв", "Эг", "Эд", "Эж", "Эй", "Эк", "Эл", "Эм", "Эн", "Эп", "Эр", "Эс", "Эт",
                        "Эф", "Эш"]
FILTERS_RU["Ю"] = ["Юг", "Юд", "Юж", "Юз", "Юл", "Юм", "Юн", "Юр", "Юс"]
FILTERS_RU["Я"] = ["Яб", "Яв", "Яг", "Яз", "Як", "Ял", "Ям", "Ян", "Яр", "Яс", "Ях"]

LAST = "последняя"
V_RAZDELE  = "В разделе"

SUFFIX_RU = dict()
SUFFIX_RU["А"] = "a_russ/0-4"
SUFFIX_RU["Б"] = "v_russ/0-5"
SUFFIX_RU["В"] = "b_russ/0-7"
SUFFIX_RU["Г"] = "g_ruus/0-8"
SUFFIX_RU["Д"] = "d_ruuss/0-9"
SUFFIX_RU["Е"] = "e_russ/0-10"
SUFFIX_RU["Ё"] = "yo_russ/0-11"
SUFFIX_RU["Ж"] = "zh_russ/0-12"
SUFFIX_RU["З"] = "z_russ/0-13"
SUFFIX_RU["И"] = "i_russ/0-14"
SUFFIX_RU["Й"] = "y_russ/0-15"
SUFFIX_RU["К"] = "k_russ/0-17"
SUFFIX_RU["Л"] = "l_russ/0-6"
SUFFIX_RU["М"] = "m_ruuss/0-18"
SUFFIX_RU["Н"] = "n_russ/0-19"
SUFFIX_RU["О"] = "n_russ/0-20"
SUFFIX_RU["П"] = "p_russ/0-21"
SUFFIX_RU["Р"] = "r_russ/0-22"
SUFFIX_RU["С"] = "s_russ/0-23"
SUFFIX_RU["Т"] = "t_russ/0-24"
SUFFIX_RU["У"] = "u_russ/0-25"
SUFFIX_RU["Ф"] = "f_russ/0-16"
SUFFIX_RU["Х"] = "h_russ/0-26"
SUFFIX_RU["Ц"] = "ts_russ/0-27"
SUFFIX_RU["Ч"] = "ch_russ/0-28"
SUFFIX_RU["Ш"] = "sh_russ/0-29"
SUFFIX_RU["Щ"] = "shch_russ/0-30"
SUFFIX_RU["Э"] = "e_russ/0-31"
SUFFIX_RU["Ю"] = "yu_russ/0-32"
SUFFIX_RU["Я"] = "ya_russ/0-33"

AUDIOKNIGI_GENRE = list()
AUDIOKNIGI_GENRE.append(["Фантастика", "fantasy"])
AUDIOKNIGI_GENRE.append(["Детективы, триллеры", "detective"])
AUDIOKNIGI_GENRE.append(["Роман, проза", "roman"])
AUDIOKNIGI_GENRE.append(["Классика", "classic"])
AUDIOKNIGI_GENRE.append(["Психология, философия", "psihologiya"])
AUDIOKNIGI_GENRE.append(["Ужасы, мистика", "uzhasy_mistika"])
AUDIOKNIGI_GENRE.append(["Аудиоспектакли", "audiospektakli"])
AUDIOKNIGI_GENRE.append(["Приключения", "priklucheniya"])
AUDIOKNIGI_GENRE.append(["История", "istoriya"])
AUDIOKNIGI_GENRE.append(["Бизнес", "business"])
AUDIOKNIGI_GENRE.append(["Эзотерика", "spirituality"])
AUDIOKNIGI_GENRE.append(["Научно-популярное", "nauchno_populyarnye"])
AUDIOKNIGI_GENRE.append(["Для детей", "detskie"])
AUDIOKNIGI_GENRE.append(["Юмор, сатира", "humor"])
AUDIOKNIGI_GENRE.append(["Ранобэ", "ranobe"])
AUDIOKNIGI_GENRE.append(["Обучение", "obuchenie"])
AUDIOKNIGI_GENRE.append(["Биографии, мемуары", "biography"])
AUDIOKNIGI_GENRE.append(["Разное", "raznoe"])
AUDIOKNIGI_GENRE.append(["На иностранных языках", "inostrannie"])
AUDIOKNIGI_GENRE.append(["Медицина, здоровье", "health"])
AUDIOKNIGI_GENRE.append(["Поэзия", "poeziya"])
AUDIOKNIGI_GENRE.append(["Религия", "religion"])
AUDIOKNIGI_GENRE.append(["Путешествия", "travel"])
