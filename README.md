# NFL Wide Receiver Performance Prediction

## Overview
This project predicts the receiving yards of an NFL wide receiver (WR) based on the defensive ranking of the opposing team. The program scrapes data from Pro Football Reference and utilizes the `nfl_data_py` Python package to gather relevant player and defensive statistics. It then applies a linear regression model to make predictions and visualizes the results.

## Features
- User input validation for player names and team names.
- Web scraping of defensive statistics from Pro Football Reference.
- Data retrieval using `nfl_data_py` for WR statistics and team information.
- Data preprocessing and merging to create a regression-ready dataset.
- Linear regression model to predict WR performance based on defensive ranking.
- Data visualization of regression results.

## Requirements
Ensure you have the following installed before running the script:

```bash
pip install pandas nfl_data_py numpy matplotlib scikit-learn beautifulsoup4 requests
```

## Usage
1. Run the script using:
   ```bash
   python script_name.py
   ```
2. Enter the name of the WR you want to analyze (e.g., `Justin Jefferson`).
3. Enter the name of the opposing defense (e.g., `Detroit Lions`).
4. The script will fetch the relevant data, train a regression model, and predict the WR's expected receiving yards.
5. A scatter plot with a trend line will be displayed, showing the relationship between defensive ranking and receiving yards.

## Data Sources
- **Pro Football Reference** (Defensive statistics)
- **nfl_data_py** (WR statistics, schedules, and team abbreviations)

## Project Structure
```
|-- Wide_Receiver_Model.py   # Main script for prediction
|-- README.md                # Project documentation
|-- requirements.txt         # List of required dependencies
```

## Future Enhancements
- Improve model accuracy by incorporating additional features such as game conditions, injuries, and home/away splits.
- Use more advanced machine learning models for better predictions.
- Develop a web-based dashboard for user interaction.

## License
This project is open-source and available for educational and non-commercial use.

