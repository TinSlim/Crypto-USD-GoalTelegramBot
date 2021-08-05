# Crypto-USD-GoalTelegramBot
Telegram Bot made to send you a message when you reach a goal with your cryptocurrencies.

# Run

1. Rename `VARIABLES-example.py` to `VARIABLES.py`.
2. Set in `VARIABLES.py` your Telegram Bot TOKEN and the admin id.
3. Execute `pip install -r requirements.txt` to install dependencies.
4. Execute `python main.py`.

# Commands

- `/make_data {currency}` : To make new data from the user, send a dictionary with the name of the currency and cuantity. Example: `/make_data {"BTCUSDT":1.03,"SHIBUSDT":200.01}`.

- `/start` : Only the admin can use this. Starts updating the currency prices.

- `/start_loop {goal}` : Starts looking if the price of the sum of your currencies exceed the goal. Example: `/start_loop 50`.

- `/end_loop` : Ends the loop made with `/start_loop`.

- `/get_total` : Returns the total USD sum of your currencies.

