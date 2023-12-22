# START/STOP ECS SERVICES

### Requirements

- This script uses python. [Click here](https://www.python.org/downloads/) to installed if you don't already have it
- Install boto3
  - `pip install boto3`
- Install python-dotenv
  - `pip install python-dotenv`

### .env Setup

> Note: Make sure the .env file is in the same directory as the other script

**Stop**

- Group your clusters and services as shown below, for example **STOP_CLUSTER_1** is grouped with **STOP_SERVICES_1**. Note the **\_1** is same for a group, increment the number for another group.
  > STOP_CLUSTER_1=test-cluster-1
  >
  > STOP_SERVICES_1=["service-test-1", "service-test-2"]
- Running the stop script
  - `python stop.py`
- Another option of running the stop script on the terminal
  - `python stop.py --cluster cluster1 --services service1 service2 service3` or
  - `python stop.py --c cluster1 --s service1 service2 service3`
    - **_Note_** This will take precedence over the env file

---

**Start**

- As before, group the clusters and services and specify the desired count for each service in the dictionary. The services in a particular cluster are listed and then each is assigned the desired count in the dict.
  > CLUSTER_1=test-cluster-1
  >
  > SERVICES_CLUSTER_1=["service-test-1", "service-test-2"]
  >
  > DESIRED_COUNTS_CLUSTER_1={"service-test-1": 1, "service-test-2": 1}
- Running the start script
  - `python start.py`
