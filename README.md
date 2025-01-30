# Gmail Rules Processor

## Prerequisites
Before running the application, ensure you have:

* Python 3.8 or higher. 
* A Google Cloud Platform account 
* Gmail API enabled in your Google Cloud Console 
* OAuth 2.0 credentials configured

## Installation
Clone the repository:
```commandline
git clone https://github.com/Nishanth-R/gmail-rules-processor.git
cd gmail-rules-processor
```

Create a virtual environment and activate it:
```commandline
python -m venv venv
venv\Scripts\activate
```
Install required packages:
```commandline
pip install -r requirements.txt
```
## Running the code 

To fetch the e-mails and to store the state - 
```commandline
python fetch_emails.py 
```
To process the rules and perform the actions in said rules - 
```commandline
python rule_processor.py
```
### Reference 
Colab notebook which contains working code
https://colab.research.google.com/drive/1CvkFPh2Mu_3UlxfdsvnZF7chb8KVLnbz?usp=sharing
