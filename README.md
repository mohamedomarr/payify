# Payify: Stock Trading Web Application

## Project demo: [Youtube demo video](https://www.youtube.com/watch?v=YpIvzdy6I8Y)

## Overview
Payify is a simulated stock trading web application where users can manage and trade stocks using virtual money. The application is built with Python, Flask, and uses PostgreSQL as a database. It leverages the IEX Cloud API to fetch real-time stock prices and information.

## Features

- **Account Registration and Authentication**: Users can register for a new account and log in to access their personal dashboard.
- **Real-Time Stock Prices**: Uses the IEX Cloud API to fetch the latest stock prices and details.
- **Stock Trading**: Allows users to buy and sell stocks. It calculates the cost of purchase or the proceeds of sale in real-time.
- **Portfolio Management**: Displays a summary of users' holdings (i.e., stocks owned along with quantities) and their current values.
- **Transaction History**: Maintains a history of all transactions a user has made, allowing users to track their activities over time.

## Installation

1. Clone the repository
```
git clone https://github.com/username/payify.git
```
2. Change into the project directory
```
cd payify
```
3. Install the requirements
```
pip install -r requirements.txt
```
4. Create the MySQL database and update the connection details in `app.py`.
5. Run the Flask application
```
flask run
```

## Usage

1. Register for a new account.
2. Use the dashboard to search for stocks.
3. Buy or sell stocks based on real-time prices.
4. View the transaction history and current portfolio from the respective pages.

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check [issues page](https://github.com/username/payify/issues) if you want to contribute.

## License

This project is licensed under the terms of the MIT license.

## Acknowledgments

- Data provided for free by [IEX Cloud](https://iexcloud.io/).
- This application is for educational purposes only and is not intended for actual trading.

## Contact

Your Name - mohamed@saadomar.com
