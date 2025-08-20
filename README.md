# FEUP - Artificial Intelligence - 2024/2025

> Curricular Unit: IA - [Inteligência Artificial](https://sigarra.up.pt/feup/pt/UCURR_GERAL.FICHA_UC_VIEW?pv_ocorrencia_id=541894)

## 3rd Year - 2nd Semester - 1st Group Project

### How to run the project

> Ensure you have Python 3.x is installed on your system.
> Also ensure that you have pip3 installed. It is included by default in Python 3.4 and later versions.

1. Clone the repository
2. Navigate to the project directory
3. Install the required dependencies

```bash
pip install uv
```

> Or another installation method as per [UV's documentation](https://docs.astral.sh/uv/getting-started/installation/)

4. Run the project

```bash
uv run woodblock
```

## Navigation

There are multiple screens in our project so we decided to write this navigation guide to help any user that finds themselves lost. This is the common navigation order for a common user:

> **Start Screen:** Welcome page, simply click anywhere on the program screen in order to proceed
>
> **Player Select Screen:** In this page you will choose wether the player will be the human user with an helper ai for hints or an ai
>
> **Algorithm Select Screen:** In this page you will select the algorithm that the ai will use, either for hints in case of a human player, or simply for an ai player
>
> **Gamemode Select Screen:** In this screen you will select if you either want to play the levels where the objective is to clear all target blocks on the screen in the least amount of moves, or the infinite gamemode where the objective is to clear the biggest amount of lines/columns before the board is filled and no available piece can be placed
>
> **Level Select Screen:** In this screen you can choose the level you wish to select. Note that even though the board is the same for the same level, the pieces are randomly generated every time the level is replayed. In case you wish to compare algorithms, you will need to select custom levels where every information about the level is stored in the custom directory

### Developed by:

1. Gabriel Carvalho - E-mail: up202208939@up.pt
2. Guilherme Silva - E-mail: up202205298@up.pt
3. Valentina Cadime - E-mail: up202206262@up.pt
