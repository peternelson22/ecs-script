# START/STOP ECS SERVICES

### Requirements

- This script uses python. [Click here](https://www.python.org/downloads/) to installed if you don't already have it
- Install boto3
  - `pip install boto3`
- Install python-dotenv
  - `pip install python-dotenv`

### .env Setup

> Note: Make sure the .env file is in the same directory as the other script

# START_V1 and STOP_V1

A more streamlined revision of the scripts - the env is simpler to work with as you only have to defined the variables in one list. The nested dict takes a `name` as key for the cluster-name and `services` as key for the inner dict which takes names of services and their corresponding number of desired_counts.

- Running the scripts
  - `python stop_v1.py`
  - `python start_v1.py`
- Another option of running the stop_v1.py script on the terminal
  - `python stop_v1.py --cluster cluster1 --services service1 service2 service3` or
  - `python stop_v1.py -c cluster1 -s service1 service2 service3`
    - **_Note_** This will take precedence over the env file

```python
CLUSTERS='[
    {
        "name": "cluster1",
        "services": {
            "service1": 2,
            "service2": 1
        }
    },
    {
        "name": "cluster2",
        "services": {
            "service1": 3,
            "service2": 4,
            "service3": 2,
        }
    },
    {
        "name": "cluster3",
        "services": {
            "service1": 2,
            "service2": 5,
            "service3": 3,
        }
    }
]'

```

# This is for stop.py and start.py **_Dont use this!!!_**

**Stop**

- Group your clusters and services as shown below, for example **STOP_CLUSTER_1** is grouped with **STOP_SERVICES_1**. Note the **\_1** is same for a group, increment the number for another group.
  > STOP_CLUSTER_1=test-cluster-1
  >
  > STOP_SERVICES_1=["service-test-1", "service-test-2"]
- Running the stop script
  - `python stop.py`
- Another option of running the stop script on the terminal
  - `python stop.py --cluster cluster1 --services service1 service2 service3` or
  - `python stop.py -c cluster1 -s service1 service2 service3`
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
