from aiogram.fsm.state import StatesGroup, State

class VideoEffectStates(StatesGroup):
    """
    Список станів, через які проходить користувач у процесі обробки відео:
    """

    # Очікуємо, поки користувач надішле відеоповідомлення
    WaitingForVideo = State()

    # Користувач обирає один із ефектів (окуляри, вибух, сердечка, сміх)
    ChoosingEffect = State()

    #Користувач обрав додати еффект вибуху та має вказати таймкод для обробки еффекту
    WaitingForExplosionTime = State()

    # Питаємо, чи додати інтро/аутро
    ChoosingAddonType = State()

    # Якщо обрано інтро/аутро — вибір джерела (готове відео чи своє)
    ChoosingAddonSource = State()

    #Чекаємо, поки користувач обере відео з бібліотеки
    ChoosingAddonFromLibrary = State()

    # Чекаємо, поки користувач надішле власне інтро/аутро
    WaitingForAddonVideo = State()

    # Стан обробки: FFmpeg/OpenCV конкатенація, накладення оверлеїв
    Processing = State()
