# Stock-Home
STOCK-HOME is a web application that provides users with real-time stock prices and allows them to simulate buying and selling stocks using virtual money. This project is built using Python, Flask, and the IEX API.

## Features
User registration and login
Real-time stock prices using the IEX API
Simulation of buying and selling stocks using virtual money
Transaction details stored in user accounts

## Installation
To run the STOCK-HOME application locally, you'll need to follow these steps:

Clone the repository: git clone https://github.com/YOUR-USERNAME/STOCK-HOME.git
Navigate to the project directory: cd STOCK-HOME
Install the required packages: pip install -r requirements.txt
Obtain an API key from Alpha Vantage: https://www.alphavantage.co/support/#api-key
Add the API key to your environment variables: export API_KEY="YOUR-API-KEY"
Run the application: python app.py

## Usage
Once the application is running, you can access it at http://localhost:5000/ in your web browser. You can register a new user account by clicking on the "Register" link on the navigation bar. After registering, you can log in using your username and password.

The home page displays a list of stocks and their current prices. You can view more information about a specific stock by clicking on its name. To simulate buying and selling stocks, click on the "Portfolio" link on the navigation bar. Here, you'll see a list of the stocks you own and their current prices. You can simulate buying and selling stocks by entering the desired quantity and clicking on the "Buy" or "Sell" button.

## Contributing
If you'd like to contribute to this project, please fork the repository and create a pull request with your changes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
