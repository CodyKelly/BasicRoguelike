import libtcodpy, prepare

def menu(input, header, options, width):	
    if len(options) > 26:
        raise ValueError("Cannot have a menu with more than 26 options")

    # Calculate total height for the header (after auto-wrap) and one line per options
    if header == "":
        header_height = 0
    else:
        header_height = libtcodpy.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
    height = len(options) + header_height

    # Create an off-screen console that represents the menu's window
    window = libtcodpy.console_new(width, height)

    # Print the header, with auto-wrap
    libtcodpy.console_set_default_foreground(window, libtcodpy.white)
    libtcodpy.console_print_rect_ex(window, 0, 0, width, height, libtcodpy.BKGND_NONE, libtcodpy.LEFT, header)

    # Print all the options
    y = header_height
    letter_index = ord("a")

    for option_text in options:
        text = "({0}) {1}".format(chr(letter_index), option_text)
        libtcodpy.console_print_ex(window, 0, y, libtcodpy.BKGND_NONE, libtcodpy.LEFT, text)
        y += 1
        letter_index += 1

    # Calculate coordinates
    x = prepare.SCREEN_WIDTH / 2 - width / 2
    y = prepare.SCREEN_HEIGHT / 2 - height / 2

    # Compute x and y offsets to convert console position to menu position
    x_offset = x # x is the left edge of the menu
    y_offset = y + header_height # The top edge of the menu

    # Now we'll blit the contents of "window" to the root console
    # The last two parameters of this next function control the foreground transparency
    # and the background transparency, respectively
    libtcodpy.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    while True:
        key = input["Key"]
        mouse = input["Mouse"]
        # Present the root console to the player and wait for a key press
        libtcodpy.console_flush()
        libtcodpy.sys_check_for_event(libtcodpy.EVENT_KEY_PRESS|libtcodpy.EVENT_MOUSE, key, mouse)
        
        if mouse.lbutton_pressed:
            (menu_x, menu_y) = (mouse.cx - x_offset, mouse.cy - y_offset)
            
            # Check if click is within the menu and on a choice
            if menu_x >= 0 and menu_x < width and menu_y >= 0 and menu_y < height - header_height:
                return menu_y
                
        if mouse.rbutton_pressed or key.vk == libtcodpy.KEY_ESCAPE:
            return None # Cancel if the player right clicked or hit escape
        
        if key.vk == libtcodpy.KEY_ENTER and key.lalt: # Check for alt + enter to fullscreen
            libtcodpy.console_set_fullscreen(not libtcodpy.console_is_fullscreen())
        
        # Convert the ASCII code to an index; if it corresponds to an option, return it
        index = key.c - ord('a')
        if index >= 0 and index < len(options): return index
        
        # If they hit a letter that is not an option, return None
        if index >= 0 and index <= 26: return None
