# CmDone

A command-line based application implemented in Python. **CmDone** provides an intuitive command-line interface to create, save, view and edit checklists based on built-in templates (a set of columns)

## Table of Contents

- [Video Demo](#video-demo)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Additional Commands](#additional-commands)
  - [View Checklists](#view-checklists)
  - [Create New Checklist](#create-checklist)
    - [Add Item](#add-item)
    - [Update Item](#update-item)
    - [Sort Table](#sort-table)
    - [Delete Item](#delete-item)
  - [Delete Checklist](#delete-checklist)
  - [Create New Template](#create-template)
  - [Deleting a Template](#delete-template)
  

### Video Demo

Watch a quick video demonstration. 

[![Cmdone video Demo](https://i.imgur.com/DcLhBSU.png)](https://youtu.be/sM22MbspZB8?si=r51qkBle6kN9s1g-)


## Features

CmDone includes the following features:

- Create Checklists based on existing or custome templates.
- Create New Templates using a set of native data types that control column behavior.
- See your current saved checklists.
- Display and update your checklists.
- Sort the current checklist based on any column.
- Delete checklists or templates.


## Prerequisites

- Python 3.10 or higher
- A terminal or command prompt
- Rich, Titlecase and Pytest (included in requirements.txt)

## Installation

1. Clone the repository or download the files:

   ```bash
   git clone https://github.com/GonzaEDS/cmdone.git
   ```

2. Navigate to the project directory:

   ```bash
   cd "cmdone"
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Inside the project directory run `project.py` to start the application:

```bash
python project.py
```
![Cmdone homepage](https://i.imgur.com/GnVD96d.png)


### Additional Commands

Entering `c` you can se the **Additional Commands** page that lists some commands you can use beside the ones that are listed at the bottom of each page. Including shortcuts for navigating to each page, from any other page. 
- `home`: Home page.
- `view`: View Checklists Page.
- `new checklist`: Create New Checklist Page.
- `new template`: Create New Template Page
- `info`: The same Additional Commands Page.

### View Checklists

To view your existing checklists:

1. Start the application.
2. Use the `view` command to navigate to the View Checklists Page, or just `v` if in thoe Home Page.
3. Select a checklist entering the corresponding number to view and edit it.


### Create New Checklist

To create a new checklist:

1. Enter `new checklist` to navigate to the Create New Checklist page.
2. Follow the prompts to select a template or create a new one.
3. Enter a name for your new checklist when prompted.
4. Your new checklist is now created. You can start adding items to it.


#### Add Item

To add a new item to your checklist:

1. While viewing a checklist, enter the `n` to add a new item.
2. Provide the necessary information for each column based on the template.
3. You can abort the process by entering `cancel`.


#### Update Item

To update an item in your checklist:

1. While viewing a checklist, enter `u` to update an item.
2. Select the item you wish to update by entering the corresponding ID.
3. For each column enter the new desired value or press `enter` to keep the same. You can about the process by entering `cancel`


#### Sort Table

To sort the items in your checklist:


1. While viewing a checklist, enter `s`.
2. Specify the column you want to sort by.
4. The checklist will be sorted accordingly.


#### Delete Item

To delete an item from your checklist:


1. While viewing a checklist, enter `d` to delete an item .
2. Select the item to delet by the ID.
3. Confirm the deletion.


### Delete Checklist

To delete an entire checklist:

1. Navigate to the View Checklists page using the `view` command.
2. Enter `d` to delete a checklist
3. Select the checklist to delete by the number.
4. Confirm the deletion.


### Create New Template

You can create your own templates, using the name you wish for the columns, while chosing any of the integrated column data types. You must include at least two columns and one and only column that marks the completion of the item. 

![Column data-types](https://i.imgur.com/8ZCWjbq.png)

To create a new checklist template:

1. From the main menu, enter `new template` to navigate to the Create New Template page.
2. Enter `n` to set the name of your template.
3. Enter `c` to add a column. 
3. Save the template. It will now be available when creating new checklists.

