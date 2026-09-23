#Этот файл тестирован только по закладкам, остальные функции с багами
from datetime import datetime
import json
import os
import re
from playwright.sync_api import sync_playwright
from playwright.sync_api import expect, TimeoutError as PlaywrightTimeoutError


# Вызов функции: result = get_value(target_urls, "MDLP", "pages", 1)

def get_value(data, *args):
    # Метод .get() защитит от ошибок, если ключа нет
    for arg in args:
        data = data[arg]
    return data
#print(get_value(target_urls, "MDLP", "pages", 1))

def get_file_name(data, *args):
    string = args[0]
    
    for arg in args:
        data = data[arg]
        
        if arg == args[-1] and isinstance(data, str):
            string += f"_{data}"
            
        elif arg == args[-1]:
            
            for d in data:
                string += f"_{d}"
        else:
            pass
            
    return string

def page_goto(url):
      
    try:
        # 1. Используем оптимальный таймаут 15 секунд
        # "networkidle" виснет, оставляем дефолтный "load", но страхуем паузой ниже
        page.goto(url, timeout=15000)
        print("Базовая страница загружена")
        
        # 2. Даем скриптам PowerBI 5 секунд, чтобы гарантированно отрисовать графики
        page.wait_for_timeout(5000)
        print("Данные и графики отрисованы")
    except PlaywrightTimeoutError:
        # 3. Теперь ошибка таймаута корректно перехватится, если сайт лежит или не ответил за 15 сек
        print("Ошибка: страница не успела загрузиться за 15 секунд")
        pass

def create_screenshot_folder():
    base_dir = "C:\\Users\\BVP_RU1\\Создать_отчет\\"
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") 
    folder_name = f"screenshot_{current_time}"
    folder_path = os.path.join(base_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    # Возвращаем путь, чтобы использовать его дальше
    return folder_path

def take_screenshot(folder, name):

    file_path = os.path.join(folder, name)
    page.mouse.move(0, 0)
    page.wait_for_timeout(3000)
    page.screenshot(path=file_path)
    

#####################################
# Сброс до дефолта                   #
####################################
def reset_to_default ():

    """Сбрасывает фильтры до базовых настроек

    """

    # Нажимаем кнопку сброса настроек толко если она активна
    try:
        # Если кнопка активна, нажимаем ее 
        button = page.locator('button.resetBtn')
        expect(button).to_be_enabled(timeout=3000)
        button.click(delay=500)

        # Ждем появления диалогового окна и кликаем Reset внутри него
        # Локатор dialog сам подождет появления, wait_for_selector здесь лишний
        button_pattern = re.compile(r"Сброс|Reset",re.I)
        dialog = page.locator(".mat-mdc-dialog-container")
        dialog.get_by_role("button", name = button_pattern, exact=True).click(delay=500, timeout=3000)
        
    except PlaywrightTimeoutError:
        # Если кнопка не появилась идем дальше
        pass
    except AssertionError:
        # Сюда код попадет, если кнопка resetBtn оказалась заблокирована (disabled)
        pass


###############################
# Закладка                    #
###############################
def select_bookmark(title_bookmark):
    button = page.locator("[data-testid='bookmarks-btn']")
    button.click(delay=500)

    option = page.locator("[data-testid='bookmark-node']").get_by_text(title_bookmark, exact=True)
    option.click(delay=200)
    page.keyboard.press("Escape")
    page.wait_for_load_state("load", timeout=60000)
    print("основной код загружен жду 10 сек")
    page.wait_for_timeout(10000) 
    print("закладка загружена")




######################################
# Простой чекбокс                    #
######################################
def select_dropdown(title_dropdown, selected_option):
    page.locator("visual-container").filter(has_text=title_dropdown).locator("i").click(delay=200)

    page.locator(".slicer-dropdown-content").get_by_text(selected_option, exact=True).click(delay=200)

    try:
        # Ждем появление спиннера максимум 1.5 секунды
        page.wait_for_selector(".circle", state="visible", timeout=5000)
        # Если появился — ждем, пока он исчезнет (тут таймаут стандартный, например 30 сек)
        page.wait_for_selector(".circle", state="hidden")
    except PlaywrightTimeoutError:
        # Если за 5 секунд крутилка не появилась, значит данные уже загрузились мгновенно
        pass
    
    #page.keyboard.press("Escape")


######################################
# Мультичекбокс без скрола           #
######################################

def select_multiple_checkboxes(title_checkbox, options_to_select: tuple):

    # Находим выпадающий список
    #pvExplorationHost > div > div > exploration > div > explore-canvas > div > div.canvasFlexBox > div > div.displayArea.disableAnimations.fitToPage > div.visualContainerHost.visualContainerOutOfFocus > visual-container-repeat > visual-container:nth-child(13) > transform > div > div.visualContent.noVisualContainerHeader.noPopOutBar > div > div > visual-modern > div > div > div.slicer-header-wrapper > div > div > h3
    checkbox_locator = page.locator("#pvExplorationHost visual-container").filter(has_text=title_checkbox)
    combobox = checkbox_locator.locator(".slicer-dropdown-menu")

    checkbox_locator.locator(".slicer-header-spacer").hover()

    button_clear = checkbox_locator.get_by_role("button", name="Clear selections")    #<div class="slicer-header-spacer"></div>
    
    # Проверяем если выбраны значения, то скидываем до дефолта #<div class="slicer-restatement">All</div>
    if combobox.locator(".slicer-restatement", has_text="All").count() > 0:
        print('ok')
        pass
    else:
        print('not ok')
        button_clear.click(force=True, delay=500)
        
    
    combobox.click(force=True, delay=200)
    #page.locator("visual-container").filter(has_text=title_checkbox).locator("i").click(force=True, delay=200)
    
    # Проходим циклом по элементам кортежа
    for option_name in options_to_select:
        # Находим строку по тексту
        
        filter_locator = page.locator(".slicerText").get_by_text(option_name, exact=True)
        filter_locator.scroll_into_view_if_needed()
        #page.locator(".slicerText").first.hover()
        # Скроллим «мыcontent» вниз на 500 пикселей
        #page.mouse.wheel(0, 200)
        filter_locator.click(force=True, delay=200)
        
    combobox.click(force=True, delay=200)


##################################
# Мультичекбокс со скролом мышью #
##################################
def select_multiple_checkboxes_scroll_mouse(title_checkbox, options_to_select: tuple, erase_method = "erase"):

    # Находим выпадающий список
    #pvExplorationHost > div > div > exploration > div > explore-canvas > div > div.canvasFlexBox > div > div.displayArea.disableAnimations.fitToPage > div.visualContainerHost.visualContainerOutOfFocus > visual-container-repeat > visual-container:nth-child(13) > transform > div > div.visualContent.noVisualContainerHeader.noPopOutBar > div > div > visual-modern > div > div > div.slicer-header-wrapper > div > div > h3
    
    checkbox_locator = page.locator("#pvExplorationHost visual-container").filter(has=page.locator(".visualTitleArea", has_text=title_checkbox))
    print(f"checkbox_locator {checkbox_locator}")

    combobox_locator = checkbox_locator.locator(".slicer-dropdown-menu")
    print(f"combobox_locator {combobox_locator}")
    aria_label_1 = combobox_locator.get_attribute("aria-label")
    print(f"aria_label_1 {aria_label_1}")
    
    combobox_locator.wait_for(state="visible", timeout=10000)
    combobox_locator.click(force=True, delay=200)
    
    listbox_locator = page.locator(f".slicerBody[aria-label*='{aria_label_1}']")

    print(f"listbox_locator {listbox_locator}")

    aria_label_2 = listbox_locator.get_attribute("aria-label")
    print(f"aria_label_2 {aria_label_2}")

    #listbox_locator = page.locator(f".slicerBody[aria-label*='{aria_label_1}']") #работает
    #listbox_locator = page.locator(".slicer-dropdown-content").filter(has=page.locator(".slicerBody", has_text=aria_label_1)) #не оаботает
    #listbox_locator = page.locator(".slicerBody").get_by_role("combobox", name=aria_label_1) #не работает

   
    button_clear_pattern = re.compile(r"Снять выделение|Clear selections",re.I)
    button_clear = checkbox_locator.get_by_role("button", name=button_clear_pattern)    #<div class="slicer-header-spacer"></div>
    
    # Проверяем если выбраны значения, то скидываем до дефолта #<div class="slicer-restatement">All</div>

    combobox_pattern = re.compile(r"Все|All",re.I)

    

    #popup_locator = page.locator(".slicerBody")
    first_item = listbox_locator.locator(".slicerText").first
    print("Текст внутри тега:", first_item.text_content())

    if combobox_locator.locator(".slicer-restatement", has_text=combobox_pattern).count() > 0:
        print('ok')
        
        pass
    else:
        print('not ok')
        if erase_method == "erase":
            print("erase")
            checkbox_locator.locator(".slicer-header-spacer").hover()
            page.wait_for_timeout(1000)
            button_clear.click(force=True, delay=500)
            combobox_locator.click(force=True, delay=200)
        else:
            print("Сброс методом двойного клика по первому элементу ('Выбрать все')")
            if first_item.is_visible():
                first_item.click(delay=200)
                first_item.click(delay=200)


        
    
    
    #page.locator("visual-container").filter(has_text=title_checkbox).locator("i").click(force=True, delay=200)
    
    # Проходим циклом по элементам кортежа
    #listbox_locator.locator(".slicerText").first.wait_for(state="visible", timeout=10000)
    page.wait_for_timeout(1000)
    first_item.click(force=True, delay=200)
    page.wait_for_timeout(500)
    first_item.click(force=True, delay=200)


    for option_name in options_to_select:
        # Находим строку по тексту
        print(f"Ищем элемент: {option_name}")
        
        # Локатор конкретной строки по тексту
        filter_locator = listbox_locator.locator(".slicerText").get_by_text(option_name, exact=True)
        attempts = 0

        # Наводим мышь на область списка, чтобы скроллинг колесиком (mouse.wheel) работал внутри него
        first_item.hover()

        while not filter_locator.is_visible() and attempts < 30:
            # Скроллим колесиком мыши строго вниз внутри открытого попапа
            page.mouse.wheel(0, 180)
            page.wait_for_timeout(100)  # Небольшая пауза, чтобы Power BI успел подгрузить строки (Lazy Load)
            attempts += 1
            
        # 7. Кликаем по найденному элементу
        if filter_locator.is_visible():
            filter_locator.scroll_into_view_if_needed() 
            filter_locator.click(force=True, delay=200)
            print(f"Успешно выбран: {option_name}")
        else:
            print(f"Предупреждение: Элемент '{option_name}' не найден в списке после прокрутки")

    # Закрываем комбобокс после завершения выбора всех элементов
    combobox_locator.click(force=True, delay=200)
    print(f"--- Фильтр {title_checkbox} успешно заполнен ---")


def select_multiple_checkboxes_scroll_mouse_GM(title_checkbox, options_to_select: tuple, erase_method = "erase"):
    print(f"\n--- Начинаем обработку фильтра: {title_checkbox} ---")

    # 1. Находим главный контейнер слайсера по заголовку
    # Используем гибкий поиск по классу заголовка, чтобы не привязываться к жесткому пути
    checkbox_locator = page.locator("#pvExplorationHost visual-container").filter(
        has=page.locator(".visualTitleArea, .slicer-header-wrapper, h3", has_text=title_checkbox)
    )
    
    # 2. Локатор кнопки комбобокса (для открытия/закрытия списка)
    combobox_locator = checkbox_locator.locator(".slicer-dropdown-menu, [role='combobox']").first
    
    # Кнопка очистки фильтра "Снять выделение"
    button_clear_pattern = re.compile(r"Снять выделение|Clear selections", re.I)
    button_clear = checkbox_locator.get_by_role("button", name=button_clear_pattern)

    # 3. Раскрываем список, чтобы считать атрибуты и проверить состояние
    combobox_locator.wait_for(state="visible", timeout=10000)
    combobox_locator.click(force=True, delay=200)
    page.wait_for_timeout(500) # Даем время на отрисовку попапа

    # ВАЖНО: Глобальный локатор для всплывающего окна Power BI
    # Элементы списка (.slicerText) теперь ищем строго внутри этого попапа!
    popup_locator = page.locator(".slicer-dropdown-popup, .dropdown-menu, body").last
    first_item = popup_locator.locator(".slicerText").first

    # 4. Сброс фильтра, если значения уже были выбраны
    combobox_pattern = re.compile(r"Все|All", re.I)
    if checkbox_locator.locator(".slicer-restatement", has_text=combobox_pattern).count() > 0:
        print('Состояние фильтра: Выбрано "Все". Сброс не требуется.')
    else:
        print('Фильтр имеет измененные значения. Выполняем сброс...')
        if erase_method == "erase":
            # Закрываем меню, чтобы навести на заголовок и нажать "Снять выделение"
            combobox_locator.click(force=True, delay=200) 
            checkbox_locator.locator(".slicer-header-wrapper, .slicer-header-spacer").hover()
            page.wait_for_timeout(500)
            if button_clear.is_visible():
                button_clear.click(force=True, delay=500)
            # Снова открываем меню для выбора новых опций
            combobox_locator.click(force=True, delay=200)
            page.wait_for_timeout(500)
        else:
            print("Сброс методом двойного клика по первому элементу ('Выбрать все')")
            if first_item.is_visible():
                first_item.click(delay=200)
                first_item.click(delay=200)

    # 5. Проверяем, открыт ли список и виден ли первый элемент
    first_item.wait_for(state="visible", timeout=10000)

    # 6. Цикл выбора нужных опций из кортежа
    for option_name in options_to_select:
        print(f"Ищем элемент: {option_name}")
        
        # Локатор конкретной строки по тексту
        filter_locator = popup_locator.locator(".slicerText").get_by_text(option_name, exact=True)
        attempts = 0

        # Наводим мышь на область списка, чтобы скроллинг колесиком (mouse.wheel) работал внутри него
        first_item.hover()

        while not filter_locator.is_visible() and attempts < 30:
            # Скроллим колесиком мыши строго вниз внутри открытого попапа
            page.mouse.wheel(0, 180)
            page.wait_for_timeout(100)  # Небольшая пауза, чтобы Power BI успел подгрузить строки (Lazy Load)
            attempts += 1
            
        # 7. Кликаем по найденному элементу
        if filter_locator.is_visible():
            filter_locator.scroll_into_view_if_needed() 
            filter_locator.click(force=True, delay=200)
            print(f"Успешно выбран: {option_name}")
        else:
            print(f"Предупреждение: Элемент '{option_name}' не найден в списке после прокрутки")
        
    # Закрываем комбобокс после завершения выбора всех элементов
    combobox_locator.click(force=True, delay=200)
    print(f"--- Фильтр {title_checkbox} успешно заполнен ---")

######################################
# Мультичекбокс со скролом стрелкой  #
######################################
def select_multiple_checkboxes_scroll(title_checkbox, options_to_select: tuple):
    # 1. Открываем выпадающий список
    button = page.locator("visual-container").filter(has_text=title_checkbox).locator(".slicer-dropdown-menu")
    button.click(force=True, delay=200)
    page.wait_for_timeout(500) # Даем списку время раскрыться
    
    # Контейнер, внутри которого физически происходит скролл
    scroll_container_selector = ".slicer-dropdown-content .slicerBody"
    if page.locator(scroll_container_selector).locator(".slicerText").first.is_visible():
        page.locator(scroll_container_selector).locator(".slicerText").first.click(delay=200)
        page.locator(scroll_container_selector).locator(".slicerText").first.click(delay=200)
    
    # 2. Проходим циклом по элементам кортежа
    for option_name in options_to_select:
        # Локатор для искомого текста
        target_locator = page.locator(scroll_container_selector).get_by_text(option_name, exact=True)
        
        # Цикл прокрутки: скроллим контейнер вниз, пока элемент не появится в DOM и не станет видимым
        attempts = 0
        # Сначала кликаем по любой видимой строчке, чтобы перевести фокус на список
        
            
        while not target_locator.is_visible() and attempts < 84:
            # Нажимаем стрелку вниз на клавиатуре
            page.keyboard.press("ArrowDown")
            page.wait_for_timeout(50)  # Быстрая прокрутка
            attempts += 1
            
        # 3. Когда элемент появился и стал видим, кликаем по нему
        if target_locator.is_visible():
            target_locator.scroll_into_view_if_needed() # Теперь сработает для точного выравнивания
            target_locator.click(force=True, delay=200)
        else:
            print(f"Предупреждение: Элемент '{option_name}' не найден в списке")
    
    button.click(force=True, delay=200)      
    page.wait_for_timeout(3000)

##################################
# Открытие правой боковой панели #
##################################
def select_filter_pane (filter_title, options_to_select: tuple):
   
    # Находим панель, а внутри неё — кнопку по её тексту 'Показать/скрыть область фильтров' или 'Show/hide filter pane'
    button = page.locator(
    "#pvExplorationHost outspace-pane button[aria-label*='Показать/скрыть область фильтров'], "
    "#pvExplorationHost outspace-pane button[aria-label*='Show/hide filter pane']"
)

    # Если кнопка неактивна, то кликаем по ней
    if button.get_attribute("aria-expanded") == 'false':
        print('false')
        button.click(force=True, delay=500)
    else:
        print('true')
        pass

    # Находим именно тот заголовок
    filter_locator = page.locator(f'#exploreFilterContainer .filterCardTitleSection:has-text("{filter_title}")')
    # Скроллим к нему
    filter_locator.scroll_into_view_if_needed()

    #Проверяем выбраны ли фильтры  и если да, то сбрасываем их
    button_clear = filter_locator.locator("button.clear")
    span_is_all = filter_locator.locator('span[data-testid="filter-card-restatement"]')
    if span_is_all.get_attribute ("title") != 'is (All)':
        print('not is All')
        button_clear.click(force=True, delay=500)


    button = filter_locator.locator("button.expand, button.collapse")
    if button.get_attribute("aria-expanded") == 'false':
        print('панель закрыта')
        button.click(force=True, delay=500)
    
#exploreFilterContainer > div.cards > div > filter:nth-child(12) > div > div.filterCardTitleSection > div.cardHeader.flex > button.glyphicon.glyph-mini.ng-star-inserted.expand
#exploreFilterContainer > div.cards > div > filter:nth-child(12) > div > div.filterCardTitleSection > div.cardHeader.flex > button.glyphicon.glyph-mini.ng-star-inserted.collapse
#exploreFilterContainer > div.cards > div > filter:nth-child(12) > div > div.filterCardTitleSection > div.cardHeader.flex > button.filterPaneIcon.clear.glyphicon.glyph-mini.pbi-glyph-eraser.ng-star-inserted
#exploreFilterContainer > div.cards > div > filter:nth-child(12) > div > div.filterCardTitleSection > div.controlPanel.flex > span
#<span _ngcontent-ng-c1887535675="" data-testid="filter-card-restatement" class="restatement trimmedTextWithEllipsis" title="is (All)" style="font-size: 9pt;">is (All)</span>
    
    # Проходим циклом по элементам кортежа
    for option_name in options_to_select:
        # Находим строку по тексту # Метод .check() сам под капотом проверяет is_checked() а click() нет, НАДО ДОБАВИТЬ!!!

        page.get_by_role("checkbox", name=option_name, exact=True).click(force=True, delay=200)

        page.wait_for_timeout(150)
            
    
##################################

def select_pages_pane(pane_title):

    """Открывает левую боковую панель и выбирает нужную вкладку.

    Аргументы:
        page: Объект страницы Playwright.
        pane_title (str): Точное название вкладки (например, "Pivot Table").
    """
    
    # Находим панель, а внутри неё — кнопку по тексту
    button = page.locator(f'exploration-fluent-navigation button[aria-label="{pane_title}"]') #это работающий вариант
    #button = page.locator("exploration-fluent-navigation").get_by_label(pane_title, exact=True) #Это тоже работающий вариант

    button.click(force=True, delay=500) 

    # Ждем пока загрузится
    page.wait_for_load_state("domcontentloaded") #надо протестировать эту опцию

##################################            
    
with sync_playwright() as p:
    # Указываем папку для сохранения сессии и отключаем флаг автоматизации
    browser = p.chromium.launch_persistent_context(channel="msedge", slow_mo=3000, user_data_dir="./user_data", headless=False,args=["--disable-blink-features=AutomationControlled"]) # Маскировка от ботов
    page = browser.new_page()
    page.set_viewport_size({"width": 1920, "height": 1080})
    target_folder = create_screenshot_folder()

    # Открываем файл в режиме чтения с явным указанием кодировки utf-8
    with open(r"C:\Users\BVP_RU1\Создать_отчет\links.json", "r", encoding="utf-8") as file:
        reports = json.load(file)
  
    
    ###select_pages_pane(get_value(target_urls,"MDLP","pages","Pivot Table"))
    ###print(get_value(target_urls,"MDLP","pages","Pivot Table"))
    ###print(target_urls.MDLP.months["10-2025"]) почему-то не работает 
    ###file_name = f"{get_file_name(target_urls,"MDLP","pages","Pivot Table")}.png"
    ###take_screenshot(target_folder, file_name)
 
    # Начало теста на закладки
    
    page_goto(get_value(reports,"MDLP","url"))

    select_bookmark(get_value(reports,"MDLP","bookmarks","Dashboard_RUB_CNTN"))
    file_name = f"{get_file_name(reports,"MDLP","bookmarks","Dashboard_RUB_CNTN")}.png"
    print(file_name)
    take_screenshot(target_folder, file_name)
    
    select_bookmark(get_value(reports,"MDLP","bookmarks","Dashboard_RUB_NWRN"))
    file_name = f"{get_file_name(reports,"MDLP","bookmarks","Dashboard_RUB_NWRN")}.png"
    print(file_name)
    take_screenshot(target_folder, file_name)

    select_bookmark(get_value(reports,"MDLP","bookmarks","Dashboard_RUB_CNTN+NWRN"))
    file_name = f"{get_file_name(reports,"MDLP","bookmarks","Dashboard_RUB_CNTN+NWRN")}.png"
    print(file_name)
    take_screenshot(target_folder, file_name)

    select_bookmark(get_value(reports,"MDLP","bookmarks","DB_RUB_1_month"))
    file_name = f"{get_file_name(reports,"MDLP","bookmarks","DB_RUB_1_month")}.png"
    print(file_name)
    take_screenshot(target_folder, file_name)


    select_bookmark(get_value(reports,"MDLP","bookmarks","Pivot_CNT_N"))
    file_name = f"{get_file_name(reports,"MDLP","bookmarks","Pivot_CNT_N")}.png"
    print(file_name)
    take_screenshot(target_folder, file_name)

    select_bookmark(get_value(reports,"MDLP","bookmarks","Pivot_NWR_N"))
    file_name = f"{get_file_name(reports,"MDLP","bookmarks","Pivot_NWR_N")}.png"
    print(file_name)
    take_screenshot(target_folder, file_name)

    select_bookmark(get_value(reports,"MDLP","bookmarks","Pivot_CNT_N+NWR_N"))
    file_name = f"{get_file_name(reports,"MDLP","bookmarks","Pivot_CNT_N+NWR_N")}.png"
    print(file_name)
    take_screenshot(target_folder, file_name)
    
    select_bookmark(get_value(reports,"MDLP","bookmarks","Dashboard_onkaspar"))
    file_name = f"{get_file_name(reports,"MDLP","bookmarks","Dashboard_onkaspar")}.png"
    print(file_name)
    take_screenshot(target_folder, file_name)

    select_bookmark(get_value(reports,"MDLP","bookmarks","Pivot_onkaspar"))
    file_name = f"{get_file_name(reports,"MDLP","bookmarks","Pivot_onkaspar")}.png"
    print(file_name)
    take_screenshot(target_folder, file_name)





    page_goto(get_value(reports,"SFE Активность CD","url"))

    select_bookmark(get_value(reports,"SFE Активность CD","bookmarks","Dashboard_month"))
    file_name = f"{get_file_name(reports,"SFE Активность CD","bookmarks","Dashboard_month")}.png"
    print(file_name)
    take_screenshot(target_folder, file_name)

    select_bookmark(get_value(reports,"SFE Активность CD","bookmarks","Worktime"))
    file_name = f"{get_file_name(reports,"SFE Активность CD","bookmarks","Worktime")}.png"
    print(file_name)
    take_screenshot(target_folder, file_name)

    page_goto(get_value(reports,"IQDATA MarketData","url"))

    select_bookmark(get_value(reports,"IQDATA MarketData","bookmarks","CNT-N, RUR, month"))
    file_name = f"{get_file_name(reports,"IQDATA MarketData","bookmarks","CNT-N, RUR, month")}.png"
    print(file_name)
    take_screenshot(target_folder, file_name)

    select_bookmark(get_value(reports,"IQDATA MarketData","bookmarks","NWR-N, RUR, month"))
    file_name = f"{get_file_name(reports,"IQDATA MarketData","bookmarks","NWR-N, RUR, month")}.png"
    print(file_name)
    take_screenshot(target_folder, file_name)
    
    page_goto(get_value(reports,"Secondary Sales Report","url"))

    select_bookmark(get_value(reports,"Secondary Sales Report","bookmarks","Distr_1_month_RUB"))
    file_name = f"{get_file_name(reports,"Secondary Sales Report","bookmarks","Distr_1_month_RUB")}.png"
    print(file_name)
    take_screenshot(target_folder, file_name)

    select_bookmark(get_value(reports,"Secondary Sales Report","bookmarks","Distr_MAT_RUB"))
    file_name = f"{get_file_name(reports,"Secondary Sales Report","bookmarks","Distr_MAT_RUB")}.png"
    print(file_name)
    take_screenshot(target_folder, file_name)

    page_goto(get_value(reports,"Stocks Distributors","url"))

    select_bookmark(get_value(reports,"Stocks Distributors","bookmarks","Stock_CNT_N"))
    file_name = f"{get_file_name(reports,"Stocks Distributors","bookmarks","Stock_CNT_N")}.png"
    print(file_name)
    take_screenshot(target_folder, file_name)

    select_bookmark(get_value(reports,"Stocks Distributors","bookmarks","Stock_NWR_N"))
    file_name = f"{get_file_name(reports,"Stocks Distributors","bookmarks","Stock_NWR_N")}.png"
    print(file_name)
    take_screenshot(target_folder, file_name)

    select_bookmark(get_value(reports,"Stocks Distributors","bookmarks","Stock_CNT_N_days"))
    file_name = f"{get_file_name(reports,"Stocks Distributors","bookmarks","Stock_CNT_N_days")}.png"
    print(file_name)
    page.mouse.click(1000, 70)
    take_screenshot(target_folder, file_name)

    select_bookmark(get_value(reports,"Stocks Distributors","bookmarks","Stock_NWR_N_days"))
    file_name = f"{get_file_name(reports,"Stocks Distributors","bookmarks","Stock_NWR_N_days")}.png"
    print(file_name)
    page.mouse.click(1000, 70)
    take_screenshot(target_folder, file_name)

    page_goto(get_value(reports,"Prices","url"))

    select_bookmark(get_value(reports,"Prices","bookmarks","Prices_CNT_N+NWR_N"))
    file_name = f"{get_file_name(reports,"Prices","bookmarks","Prices_CNT_N+NWR_N")}.png"
    print(file_name)
    take_screenshot(target_folder, file_name)



    


    browser.close()
    # Конец теста


    #select_pages_pane(page, "Pivot Table")
    #page.wait_for_load_state("networkidle", timeout=60000)
    #page.wait_for_load_state("domcontentloaded")

    #reset_to_default()

    ###select_dropdown("Measure", "Units")

    ###options_BU = ("Armedic", "Medical", "Medimix", "Oncology", "Pharma" )
    ###select_multiple_checkboxes("Business Unit", options_BU)

    ###options_month = ("May.2026", )
    ###select_multiple_checkboxes_scroll("Month-Week-Day", options_month)

    

    ###options_region = ("CNT-N", )
    ###select_filter_pane("Region", options_region)
    ###file_name = "Pivot table_CNT_N.png"
    ###take_screenshot(target_folder, file_name)

    ###options_region = ("NWR-N", )
    ###select_filter_pane("Region", options_region)
    ###file_name = "Pivot table_NWR-N.png"
    ###take_screenshot(target_folder, file_name)

    ###options_region = ("CNT-N", "NWR-N")
    ###select_filter_pane("Region", options_region)
    ###file_name = "Pivot table_CNT_N + NWR-N.png"
    ###take_screenshot(target_folder, file_name)


    # Вызов функции с передачей опций
    ###select_dropdown("Measure", "Units")
    
    # Вызов функции с передачей кортежа опций
    ###options_BU = ("Armedic", "Medical", "Medimix", "Oncology", "Pharma" )
    ###select_multiple_checkboxes("Business Unit", options_BU)
    
    # Вызов функции с передачей кортежа опций
    ###options_region = ("CNT-N", "NWR-N", "Select all")
    ###select_filter_pane("Region", options_region) 

    ###select_pages_pane("RBP and Targets")

    
    ###file_name = "pict_screenshot_1.png"

    # Вызов функции скрин экрана
    ###take_screenshot(target_folder, file_name)

    ###page_goto(target_urls[1])
    ###page.wait_for_load_state("domcontentloaded")

    
    ###options_month = ("May.2026", )
    ###select_multiple_checkboxes_scroll_mouse("Месяц", options_month)
    ###file_name = "SFE_Активность_CD_Dashboard.png"
    ###take_screenshot(target_folder, file_name)
    
    ###select_pages_pane("Рабочее время")
    ###file_name = "SFE_Активность_CD_Рабочее время.png"
    ###take_screenshot(target_folder, file_name)

    ###page_goto(target_urls[0])
    ###option = "Dashboard_RUB_CNTN"
    ###file_name = f"{option}.png"
    ###select_bookmark(option)
    ###take_screenshot(target_folder, file_name)
   

'''
    reset_to_default()
    select_pages_pane("Overview (diagrams)")
    page.wait_for_load_state("domcontentloaded",timeout=60000)
    options_month = ("04-2026", )
    select_multiple_checkboxes_scroll_mouse("Month", options_month, "first")
    options_market = ("CMVD w/o aGLP-1 & antiobesity", )
    select_multiple_checkboxes_scroll_mouse("Market Servier", options_market, "first")
    options_reg = ("CNT-N", )
    select_multiple_checkboxes_scroll_mouse("Geography", options_reg, "first")

    file_name = "CMVD_CNT_N.png"
    take_screenshot(target_folder, file_name)

    options_reg = ("CNT-N", "NWR-W")
    select_multiple_checkboxes_scroll("Geography", options_reg)

    file_name = "CMVD_NWR_N.png"
    take_screenshot(target_folder, file_name)'''


    

'''
# функция для CMVD не работает 
    page_goto(target_urls[2])
    reset_to_default()
    select_pages_pane("Overview (diagrams)")
    page.wait_for_load_state("networkidle")
    options_month = ("04-2026", )
    select_multiple_checkboxes("Month", options_month)
    options_market = ("CMVD w/o aGLP-1 & antiobesity", )
    select_multiple_checkboxes_scroll("Market Servier", options_market)
    options_reg = ("CNT-N", )
    select_multiple_checkboxes_scroll_mouse("Geography", options_reg)

    file_name = "CMVD_CNT_N.png"
    take_screenshot(target_folder, file_name)

    options_reg = ("CNT-N", "NWR-W")
    select_multiple_checkboxes_scroll("Geography", options_reg)

    file_name = "CMVD_NWR_N.png"
    take_screenshot(target_folder, file_name)
'''
    



#content > tri-shell > tri-item-renderer > tri-extension-page-outlet > div:nth-child(2) > report > exploration-container > div > div > docking-container > div > div > exploration-fluent-navigation > section > nav > mat-action-list > button:nth-child(3) 
#content > tri-shell > tri-item-renderer > tri-extension-page-outlet > div:nth-child(2) > report > exploration-container > div > div > docking-container > div > div > exploration-fluent-navigation > section > nav > mat-action-list > button.mat-mdc-list-item.mdc-list-item.exploration-fluent-li.item.trimmedTextWithEllipsis.fluentTheme-sm-reg.mat-mdc-list-item-interactive.mat-mdc-list-item-single-line.mdc-list-item--with-one-line.ng-star-inserted.selected > span > span > span








