from abc import ABC, abstractmethod

class BaseEffect(ABC):
    """
    Абстрактний базовий клас для відеоефектів.
    Кожен ефект має реалізувати метод apply().
    """

    @abstractmethod
    async def apply(self, input_path: str, output_path: str) -> None:
        """
        Застосовує ефект до вхідного відео і зберігає результат.

        :param input_path: шлях до вихідного відео (mp4)
        :param output_path: шлях до обробленого відео (mp4)
        """
        pass
