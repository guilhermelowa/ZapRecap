from app.services.chatgpt_utils import parse_themes_response


def test_parse_themes_response():
    # Test input
    test_response = {
        "temas": [
            {
                "tema": "Atividades cotidianas e planejamento de tarefas",
                "exemplos": [
                    "maic willians: vou sair pra ensaiar ainda",
                    "guilherme: vou tentar fazer uma janta",
                    "maic willians: vou só ajeitando as coisas aqui",
                ],
            },
            {
                "tema": "Jogos e entretenimento",
                "exemplos": [
                    "guilherme: eu joguei a primeira hoje",
                    "maic willians: a gente tá jogando lol",
                    "maic willians: vou botar ela pra jogar um gbzinho",
                ],
            },
        ]
    }

    result = parse_themes_response(test_response)

    # Assertions
    assert len(result) == 2
    assert "Atividades cotidianas e planejamento de tarefas" in result
    assert "Jogos e entretenimento" in result
    assert (
        "maic willians: vou sair pra ensaiar ainda"
        in result["Atividades cotidianas e planejamento de tarefas"]
    )
    assert "guilherme: eu joguei a primeira hoje" in result["Jogos e entretenimento"]

    # Test empty input
    assert parse_themes_response({}) == {}

    # Test malformed input
    assert parse_themes_response({"invalid": "data"}) == {}


def test_parse_themes_response_english():
    # Test input with English keys
    test_response = {
        "themes": [
            {
                "theme": "Daily activities and task planning",
                "examples": [
                    "maic willians: going to rehearsal now",
                    "guilherme: will try to make dinner",
                    "maic willians: just organizing things here",
                ],
            },
            {
                "theme": "Games and entertainment",
                "examples": [
                    "guilherme: I played the first one today",
                    "maic willians: we're playing lol",
                    "maic willians: gonna make her play some gb",
                ],
            },
        ]
    }

    result = parse_themes_response(test_response)

    # Assertions
    assert len(result) == 2
    assert "Daily activities and task planning" in result
    assert "Games and entertainment" in result
    assert "maic willians: going to rehearsal now" in result["Daily activities and task planning"]
    assert "guilherme: I played the first one today" in result["Games and entertainment"]


def test_parse_themes_response_portuguese_exemplo():
    example_response = {
        "temas": [
            {"tema": "Eventos e Shows", "exemplo": "josé edson: depois do show vou de japa"},
            {
                "tema": "Trabalho e Carreira",
                "exemplo": "guilherme: po 2k pra trabalhar 40h programando é taca fjkfkfkddk",
            },
        ]
    }

    result = parse_themes_response(example_response)
    assert len(result) == 2
    assert "Eventos e Shows" in result
    assert "Trabalho e Carreira" in result
    assert "josé edson" in result["Eventos e Shows"]
    assert "guilherme" in result["Trabalho e Carreira"]
