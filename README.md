# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/andgineer/docker-amazon-dash-button-hack/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                    |    Stmts |     Miss |   Cover |   Missing |
|------------------------ | -------: | -------: | ------: | --------: |
| src/action.py           |      113 |       15 |     87% |70-71, 73, 106, 123, 131-132, 136-137, 146-147, 173-176, 180-183 |
| src/amazon\_dash.py     |       66 |        6 |     91% |     81-86 |
| src/google\_api.py      |       24 |        0 |    100% |           |
| src/google\_calendar.py |       58 |        4 |     93% |41-42, 112, 116 |
| src/google\_sheet.py    |       77 |       58 |     25% |22-31, 40-45, 49-51, 61, 73-75, 86-106, 117-130, 137-148, 155-169, 176, 191-211, 215-244, 251-263, 267 |
| src/ifttt.py            |       21 |        0 |    100% |           |
| src/openhab.py          |       20 |        0 |    100% |           |
| src/version.py          |        1 |        0 |    100% |           |
|               **TOTAL** |  **380** |   **83** | **78%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/andgineer/docker-amazon-dash-button-hack/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/andgineer/docker-amazon-dash-button-hack/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/andgineer/docker-amazon-dash-button-hack/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/andgineer/docker-amazon-dash-button-hack/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fandgineer%2Fdocker-amazon-dash-button-hack%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/andgineer/docker-amazon-dash-button-hack/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.