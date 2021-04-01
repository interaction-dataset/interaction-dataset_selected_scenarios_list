# interaction-dataset_selected_scenarios_list

This page contains selected scenario lists of the dataset and related tool codes for different usage. we are welcome anyone interested to submit their own lists and tool code. If you are interested to do so, please email to <info@interaction-dataset.com>.

## Scenario List Format

To help users get a better understanding and easily process the scenario list, we are providing the scenario list format here. It is a recommended format since different selections may interest in different aspects, which is hard to be covered in one format. However, we do recommend saving it as csv file with the first four terms keep as provided form.

The format is given with example as following:
```csv
Scenario,File_id,StartTime_ms,EndTime_ms,Ego_agent_id,Reactive_agent_id,Agent_with_right_of_way
DR_USA_Roundabout_FT,000,6000,13600,13,12,12
```

## Directory Structure Tree

We'd like each submission to keep a similar directory structure as follows. You can also add more folders if needed.
```bash
[Name of submition]
├─README.md
├─Scenario_Lists
|      ├─Scenario_List_01.csv
|      ├─...
├─tool_code
|      ├─README.md
|      ├─scripts
|      |      ├─...
```
