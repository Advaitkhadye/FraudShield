FraudShield

This is FraudShield, a project I built to spot fraudulent transactions using machine learning.
Think of it as a little AI-powered shield that tells you if a transaction looks suspicious or totally fine .

 What it actually does

You can test one transaction at a time — just punch in the details (type, amount, balances) and FraudShield will give you an answer right away.

Or, if you’ve got a whole CSV file full of transactions, you can upload it and FraudShield will scan through everything in one go.

The best part? You can download a clean PDF report showing all the results so you don’t have to keep rerunning checks.

Under the hood

There’s a trained machine learning model (fraud_detection_pipeline.pkl) doing the heavy lifting.
It looks at things like:

transaction type

how much money is moving

balances before and after (sender + receiver)

Then it predicts whether the transaction is:

🚩 Fraudulent

✅ Legitimate
