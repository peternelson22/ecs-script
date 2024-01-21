# START/STOP ECS SERVICES

### Requirements

- This script uses python. [Click here](https://www.python.org/downloads/) to installed if you don't already have it
- Install boto3
  - `pip install boto3`
- Install python-dotenv
  - `pip install python-dotenv`
  - `pip install colorama`

### .env Setup

> Note: Make sure the .env file is in the same directory as the other script

# MAJOR UPDATE!!!

## start_tag.py and stop_tag.py

This version uses tags instead of cluster names and service names. In the `stop_tag.py`, only the cluster tags are used. If all the clusters have the same tag, it will stop all clusters having that tag. The tags are passed in a list if you have different unique tags.

- env file:

```python
STOP_TAGS='[
    {"key": "env", "value": "prod"},
    {"key": "env", "value": "dev"}
]
```

In the `start_tag.py`, since different services have different desired count, this adds a bit of complexity. In addition to the cluster tags, each service is identified with a unique tag value and then assigned a desired count. The good thing about this approach is that if the name of the service changes, the unique tag value will still be valid. Despite the tedious task of identifying and entering unique values for each service, you just have to do it once.
Additionally, all clusters with the same tag_key and tag_value can have all the services in the same dict whether the services belongs to the same cluster or not!

- env file:

```python
CLUSTERS='[
    {
        "tag_key": "env",
        "tag_value": "prod",
        "services": {
            "service1": 2,
            "service2": 1,
            "service3": 2
        }
    },
    {
        "tag_key": "env",
        "tag_value": "dev",
        "services": {
            "service4": 2
        }
    }
]'
```

**_NOTE_**: You should have a single env file

####################################################################################################################

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

# This below is for stop.py and start.py **_Dont use this!!!_**

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
