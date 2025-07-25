
from . import lv_pm
import lvgl as lv
import uctypes

POPUP_TOP_HEIGHT = 15


# I strongly advise against using user_data argument in Micropython for that purpose.
# user_data is used internally by the Micropython Bindings.
# You should keep the user_data argument as None in 99% of the cases.
# anim_datas = {}

appear_anim = lv.anim_t()
disAppear_anim = lv.anim_t()


class anim_data():
    def __init__(self, page, cb, options):
        self.page = page
        self.cb = cb
        self.options = options

# ----------------------------------------------------------------------------------------------------------
# slide animation
# ----------------------------------------------------------------------------------------------------------

def _pm_slide_appear(anim_data: anim_data):
    width = lv.screen_active().get_width()
    appear_anim.init()
    appear_anim.set_var(anim_data.page.page)

    if anim_data.page.__back:
        appear_anim.set_values(-width, 0)
    else:
        appear_anim.set_values(width, 0)

    appear_anim.set_path_cb(lv.anim_t.path_ease_out)
    appear_anim.set_time(500)
    appear_anim.set_repeat_count(1)
    appear_anim.set_custom_exec_cb(lambda a,val: anim_data.page.page.set_x(val))
    appear_anim.set_completed_cb(lambda a: anim_data.cb(anim_data.page, anim_data.options))
    appear_anim.start()

def _pm_slide_disAppear(anim_data: anim_data):
    width = lv.screen_active().get_width()
    disAppear_anim.init()
    disAppear_anim.set_var(anim_data.page.page)

    if anim_data.page.__back:
        disAppear_anim.set_values(0, width)
    else:
        disAppear_anim.set_values(0, -width)

    disAppear_anim.set_time(500)
    disAppear_anim.set_repeat_count(1)
    disAppear_anim.set_custom_exec_cb(lambda a,val: anim_data.page.page.set_x(val))
    disAppear_anim.set_completed_cb(lambda a: anim_data.cb(anim_data.page, anim_data.options))
    disAppear_anim.set_path_cb(lv.anim_t.path_ease_out)
    disAppear_anim.start()

# ----------------------------------------------------------------------------------------------------------
#   popup animation
# ----------------------------------------------------------------------------------------------------------
def _pm_popup_appear(anim_data: anim_data):
    height = lv.screen_active().get_height()
    appear_anim.init()
    appear_anim.set_var(anim_data.page.page)

    # if anim_data.page.__back:
    #     appear_anim.set_values(5, 0)
    #     anim_data.page.page.set_style_radius(0, lv.STATE.DEFAULT)
    # else:
    #     appear_anim.set_values(height, POPUP_TOP_HEIGHT)
    #     anim_data.page.page.set_style_radius(10, lv.STATE.DEFAULT)

    if anim_data.page.__back:
        appear_anim.set_values(0, 0)
    else:
        appear_anim.set_values(height, 0)

    appear_anim.set_path_cb(lv.anim_t.path_ease_out)
    appear_anim.set_time(500)
    appear_anim.set_repeat_count(1)
    appear_anim.set_custom_exec_cb(lambda a,val: anim_data.page.page.set_y(val))
    appear_anim.set_completed_cb(lambda a: anim_data.cb(anim_data.page, anim_data.options))
    appear_anim.start()

def _pm_popup_disAppear(anim_data: anim_data):
    height = lv.screen_active().get_height()
    disAppear_anim.init()
    disAppear_anim.set_var(anim_data.page.page)

    # if anim_data.page.__back:
    #     disAppear_anim.set_values(POPUP_TOP_HEIGHT, height)
    #     anim_data.page.page.set_style_radius(0, lv.STATE.DEFAULT)
    # else:
    #     disAppear_anim.set_values(0, 5)
    #     anim_data.page.page.set_style_radius(10, lv.STATE.DEFAULT)

    if anim_data.page.__back:
        disAppear_anim.set_values(0, height)
    else:
        disAppear_anim.set_values(0, 0)

    disAppear_anim.set_time(500)
    disAppear_anim.set_repeat_count(1)
    disAppear_anim.set_custom_exec_cb(lambda a,val: anim_data.page.page.set_y(val))
    disAppear_anim.set_completed_cb(lambda a: anim_data.cb(anim_data.page, anim_data.options))
    disAppear_anim.set_path_cb(lv.anim_t.path_ease_out)
    disAppear_anim.start()

# ----------------------------------------------------------------------------------------------------------
#   fade animation
# ----------------------------------------------------------------------------------------------------------

def _pm_fade_in(anim_data: anim_data):
    appear_anim.init() 
    appear_anim.set_var(anim_data.page.page)

    appear_anim.set_values(lv.OPA.TRANSP, lv.OPA.COVER)

    appear_anim.set_time(1000)
    appear_anim.set_repeat_count(1)
    appear_anim.set_path_cb(lv.anim_t.path_ease_out)
    appear_anim.set_custom_exec_cb(lambda a,val: anim_data.page.page.set_style_opa(val, lv.STATE.DEFAULT))
    appear_anim.set_completed_cb(lambda a: anim_data.cb(anim_data.page, anim_data.options))
    appear_anim.start()

def _pm_fade_out(anim_data: anim_data):
    disAppear_anim.init()
    disAppear_anim.set_var(anim_data.page.page)

    disAppear_anim.set_values(lv.OPA.COVER, lv.OPA.TRANSP)

    disAppear_anim.set_time(1000)
    disAppear_anim.set_repeat_count(1)
    disAppear_anim.set_custom_exec_cb(lambda a,val: anim_data.page.page.set_style_opa(val, lv.STATE.DEFAULT))
    disAppear_anim.set_completed_cb(lambda a: anim_data.cb(anim_data.page, anim_data.options))
    disAppear_anim.set_path_cb(lv.anim_t.path_ease_out)
    disAppear_anim.start()

def _pm_anim_appear(pm_page, behavior, cb):
    if (not behavior) or behavior == lv_pm.open_options.ANIM_NONE:
        cb(pm_page, behavior)
        return True
    
    tmp = anim_data(pm_page, cb, behavior)
    if behavior == lv_pm.open_options.ANIM_SLIDE:
        _pm_slide_appear(tmp)
    elif behavior == lv_pm.open_options.ANIM_FADE:
        _pm_fade_in(tmp)
    elif behavior == lv_pm.open_options.ANIM_POPUP:
        _pm_popup_appear(tmp)
    else:
        cb(pm_page, behavior)

def _pm_anim_disAppear(pm_page, behavior, cb):
    if (not behavior) or behavior == lv_pm.open_options.ANIM_NONE:
        cb(pm_page, behavior)
        return True
    tmp = anim_data(pm_page, cb, behavior)

    if behavior == lv_pm.open_options.ANIM_SLIDE:
        _pm_slide_disAppear(tmp)
    elif behavior == lv_pm.open_options.ANIM_FADE:
        _pm_fade_out(tmp)
    elif behavior == lv_pm.open_options.ANIM_POPUP:
        _pm_popup_disAppear(tmp)
    else:
        cb(pm_page, behavior)


