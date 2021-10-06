# Context

This scheduled take-home assignment is dedicated to helping us understand your approach to problem solving while ensuring that we protect your time. We know you are busy and appreciate you working on this short assignment for us!

We’d like you to spend at most 5 hours on this project, even if you are unable to complete it - that’s fine! We just want to get a sense for how you tackle these types of engineering problems. If you’d like, you are welcome to split the 5-hours into multiple chunks of time -- whatever works best for your schedule or working style.

After the 5 hours, please send us your GitHub repository for the assignment.

We will schedule a 30-minute session to walk through the assignment with you- this will be a great opportunity to discuss anything that you didn’t have time to document in your README.
Data Tracker

Please create a simple web service to track data.

Requirements for your web app:

    The app will query data from a publicly available source every 1 minute (try https://docs.cryptowat.ch/rest-api/ to get the latest cryptocurrency quotes, but feel free to choose any other source).

    The app will have a REST or GraphQL API to enable the following user experience (no user interface required):
        - Users will select one of the collected metrics (e.g. BTC/USD price) from a combo box or list.
        - The selected metric will be presented in a chart over time (so as to show the user how it changed throughout the last 24 hours).
        - In addition, the application will present the selected metric's "rank". The "rank" of the metric helps the user understand how the metric is changing relative to other similar metrics, as measured by the standard deviation of the metric over the last 24 hours. For example in the crypto data source, if the standard deviations of the volume of BNT/BTC, GOLD/BTC and CBC/ETH were 100, 200 and 300 respectively, then rank(CBC/ETH)=1/3, rank(GOLD/BTC)=2/3 and rank(BNT/BTC)=3/3.

Please use Python or Java and feel free to take advantage of any framework, AWS service or library you deem fit.

The key is to build a very simple version (so no need to spend a ton of time on this...), and document concrete suggestions on how to make it production ready and scalable.

We'll be paying close attention to your README with running instructions, TODOs, architecture, and potential enhancements — so it's worth spending time writing it up.

In your README, please explicitly address:

    Scalability:
        what would you change if you needed to track many metrics?
        What if you needed to sample them more frequently?
        what if you had many users accessing your dashboard to view metrics?

    Testing: how would you extend testing for an application of this kind (beyond what you implemented)?

    Feature request: to help the user identify opportunities in real-time, the app will send an alert whenever a metric exceeds 3x the value of its average in the last 1 hour. For example, if the volume of GOLD/BTC averaged 100 in the last hour, the app would send an alert in case a new volume data point exceeds 300. Please write a short proposal on how you would implement this feature request.
