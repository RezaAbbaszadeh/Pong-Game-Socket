import cx_Freeze

executable = [cx_Freeze.Executable("game.py")]

cx_Freeze.setup(
    name="game",
    options={"build_exe": {"packages":["pygame"] , "include_files":["ball.png", "player.jpg", "pong icon.png"]}},
    executables=executable
)
