from aiogram.fsm.state import State, StatesGroup


class LangState(StatesGroup):
    choosing = State()


class RegisterState(StatesGroup):
    asking_name = State()
    asking_type = State()
    asking_phone = State()
    asking_company = State()
    asking_region = State()
    asking_district = State()
    asking_address_detail = State()
    asking_account_number = State()


class RequestState(StatesGroup):
    choosing_category = State()
    choosing_type = State()
    writing = State()


class AdminReplyState(StatesGroup):
    waiting_text = State()


class EditProfileState(StatesGroup):
    choosing_field = State()
    editing_name = State()
    editing_phone = State()
    editing_region = State()
    editing_district = State()
    editing_address = State()
    editing_account_number = State()
