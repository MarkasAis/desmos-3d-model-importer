from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
import pyperclip
import desmos_compiler as DC

import time

initialized = False

browser = None
actions = None

expression_list = None
last_folder = None

edit_mode = False


def start():
    global browser, actions, expression_list, initialized
    chrome_options = Options()
    chrome_options.add_argument("--window-size=800,400")
    browser = webdriver.Chrome(chrome_options=chrome_options, executable_path="D:\\chromedriver.exe")
    actions = ActionChains(browser)
    browser.get("https://www.desmos.com/calculator")
    expression_list = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "dcg-expressionlist")))
    expression_list = expression_list.find_element_by_xpath("./child::span[1]")
    initialized = True


def end_block():
    if not initialized:
        return

    actions.reset_actions()
    actions.send_keys(Keys.ENTER).perform()


def move_right():
    if not initialized:
        return

    actions.reset_actions()
    actions.send_keys(Keys.RIGHT).perform()


def select_all():
    if not initialized:
        return

    actions.reset_actions()
    actions.send_keys(Keys.CONTROL, "a", Keys.CONTROL).perform()


def delete_all():
    if not initialized:
        return

    actions.reset_actions()
    actions.send_keys(Keys.CONTROL, "a", Keys.CONTROL, Keys.BACK_SPACE).perform()


def backspace():
    if not initialized:
        return

    actions.reset_actions()
    actions.send_keys(Keys.BACK_SPACE).perform()


def start_comment():
    if not initialized:
        return

    actions.reset_actions()
    actions.send_keys('"').perform()


def comment(text):
    start_comment()
    write(text)
    end_block()


def move_to_expression_by_id(id):
    if not initialized:
        return

    actions.reset_actions()
    actions.move_to_element(get_expression_by_id(id)).perform()
    time.sleep(0.05)
    return get_expression_by_id(id)


def get_expression_by_id(id):
    return WebDriverWait(expression_list, 1).until(EC.presence_of_element_located((By.XPATH, "./child::div[@expr-id='" + str(id) + "']")))


def get_expression_id(element):
    return element.get_attribute("expr-id")


def get_selected_expression():
    return expression_list.find_element_by_class_name("dcg-selected")


def get_selected_id():
    return get_expression_id(get_selected_expression())


def click_selected():
    block = get_selected_expression()
    block.click()
    return block


def click_last():
    block = expression_list.find_element_by_xpath("./child::div[last()]")
    block.click()
    return block


def write(value):
    if not initialized:
        return

    pyperclip.copy(value)
    actions.reset_actions()
    actions.send_keys(Keys.CONTROL, "v", Keys.CONTROL).perform()


def write_equation(equation):
    compiled = DC.compile_equation(equation)
    write(compiled)
    end_block()
    return compiled


def define_variable(name, value, min_value=None, max_value=None, step=None):
    if not initialized:
        print("Could not define variable.")
        return None

    DC.define_custom_variable(name)
    equation = name + "=" + str(value)
    compiled = DC.compile_equation(equation)
    try:
        block = WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "dcg-selected")))
        block.click()
        write(compiled)
        print("Defined variable: ", equation, "   as   ", compiled)

        if min_value is not None:
            try:
                options_message = "Options: "
                options = WebDriverWait(block, 1).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "dcg-math-field")))

                if len(options) != 3:
                    raise NoSuchElementException

                options[0].click()
                write(min_value)
                options_message += "min=" + str(min_value)

                if max_value is not None:
                    options[1].click()
                    write(max_value)
                    options_message += ", max=" + str(max_value)

                    if step is not None:
                        options[2].click()
                        write(step)
                        options_message += ", step=" + str(step)

                print(options_message)
                end_block()
            except TimeoutException:
                print("Could not define variable options.")

        end_block()
        return compiled
    except TimeoutException:
        print("Could not define variable.")
        return None


def define_function(name, parameters, value):
    if not initialized:
        print("Could not define function.")
        return None

    DC.define_custom_function(name)
    equation = name + "("
    for i in range(len(parameters)):
        equation += parameters[i]
        if i < len(parameters)-1:
            equation += ","

    equation += ")=" + value
    compiled = DC.compile_equation(equation)
    try:
        block = WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "dcg-selected")))
        block.click()
        write(compiled)
        print("Defined function: ", equation, "   as   ", compiled)
        end_block()
        return compiled
    except TimeoutException:
        print("Could not define function.")
        return None


def flip_table(table):
    normal_row_count = len(table[0])
    normal_col_count = len(table)

    flipped_table = [[0] * normal_col_count for i in range(normal_row_count)]

    for flipped_column in range(normal_row_count):
        for flipped_row in range(normal_col_count):
            flipped_table[flipped_column][flipped_row] = table[flipped_row][flipped_column]

    return flipped_table


def define_table(names, values, columns_first=False):
    if not initialized:
        return

    try:
        WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "dcg-add-expression-btn"))).click()
        WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "dcg-action-newtable"))).click()
        block = click_selected()
        table = WebDriverWait(block, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "dcg-tabledata")))

        if not columns_first:
            values = flip_table(values)

        print("Loading table of dimensions: ", len(values), "x", len(values[0]))

        top_row = table.find_element_by_xpath("./child::tr[1]")
        first_cell = top_row.find_element_by_xpath("./child::div[1]/child::span[1]/child::span[2]")
        first_cell.click()
        delete_all()

        for i in range(len(names)):
            DC.define_table_variable(names[i])
            write(DC.compile_name(names[i]))
            if i > 0:
                time.sleep(0.05)
                disable_visuals_button = top_row.find_element_by_xpath("./child::div[contains(@class, 'dcg-selected')]/"
                                                                       "child::div[2]/child::div[1]/child::span[1]/"
                                                                       "child::i[1]")
                disable_visuals_button.click()
            move_right()

        move_right()

        for row in range(len(values[0])):
            for col in range(len(values)):
                write(DC.compile_equation(values[col][row]))
                move_right()

            move_right()
            print("Imported ", (row+1)*len(values), " out of ", len(values)*len(values[0]), " element(s).")

        end_block()
    except (NoSuchElementException, TimeoutException):
        print("Could not define table.")


def define_polygon(points):
    compiled = "\\operatorname{polygon}\\left("
    for i in range(len(points)):
        compiled += "\\left(" + DC.compile_equation(points[i][0]) + "," + DC.compile_equation(points[i][1]) + "\\right)"

        if i < len(points)-1:
            compiled += ","

    compiled += "\\right)"
    block = click_selected()
    write(compiled)
    end_block()
    id = get_expression_id(block)
    print("Defined polygon with points ",  points, ",   ID: ", id, ",   as   ", compiled)
    return id


def create_folder(name):
    global last_folder
    WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "dcg-add-expression-btn"))).click()
    WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "dcg-action-newfolder"))).click()
    block = click_selected()
    write(name)
    end_block()
    last_folder = get_expression_id(block)
    print("Created folder named '", name, "',   ID: ", last_folder)
    return block


def close_folder(id):
    folder = move_to_expression_by_id(id)
    WebDriverWait(folder, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "dcg-icon-caret-down"))).click()


def end_folder(close=True):
    global last_folder
    if last_folder is not None:
        backspace()
        if close:
            close_folder(last_folder)

        last_folder = None


def toggle_edit_mode():
    global edit_mode
    edit_button = WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "dcg-action-toggle-edit")))
    edit_button.click()
    edit_mode = not edit_mode
    if not edit_mode:
        click_last()


def toggle_expression_edit_mode(id):
    global edit_options_block
    block = move_to_expression_by_id(id)
    edit_button = block.find_element_by_class_name("dcg-circular-icon-container")
    edit_button.click()
    try:
        edit_options_block = browser.find_element_by_class_name("dcg-exp-options-menu")
    except NoSuchElementException:
        edit_options_block = None


def toggle_wireframe():
    if edit_options_block is not None:
        edit_options_block.find_element_by_class_name("dcg-toggle-view").click()
    else:
        print("Could not toggle wireframe. Expression edit mode is not active.")


def toggle_face():
    if edit_options_block is not None:
        edit_options_block.find_element_by_class_name("dcg-icon-check").click()
    else:
        print("Could not toggle face. Expression edit mode is not active.")


def set_color(color):
    if edit_options_block is not None:
        color_menu = edit_options_block.find_element_by_class_name("dcg-color-menu")
        color_menu.find_element_by_xpath("./child::span[" + str(color) + "]").click()
    else:
        print("Could not change color. Expression edit mode is not active.")


def set_degree_mode():
    if not initialized:
        return

    try:
        tool_button = WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "dcg-settings-pillbox")))
        tool_button.click()
        WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "dcg-action-degreemode"))).click()
        tool_button.click()
    except TimeoutException:
        print("Could not switch to degree mode.")


def set_radian_mode():
    if not initialized:
        return

    try:
        tool_button = WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "dcg-settings-pillbox")))
        tool_button.click()
        WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "dcg-action-radianmode"))).click()
        tool_button.click()
    except TimeoutException:
        print("Could not switch to radian mode.")

