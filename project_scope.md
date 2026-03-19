# Project Scope

## Project Title
**Book Metadata, Review & Insight API**

## Overview
This project aims to design and implement a data-driven Web API for book metadata management, user reviews, reading list tracking, and analytical insights. In addition to standard CRUD functionality, the system supports importing metadata from a real public source and provides personalised recommendations based on user activity and stored review data.

## Objectives
The main objectives of the project are to:
- provide a structured RESTful API for managing books and related entities
- allow users to create, view, update, and manage book reviews
- support personal reading list management
- import and normalise book metadata from a public data source
- expose analytics endpoints for exploring patterns in ratings, genres, and user preferences
- generate personalised recommendations using explainable recommendation logic

## Target Users
The API is intended for two primary user groups:

### General Users
General users can:
- browse and search books
- create and manage reviews
- maintain their own reading lists
- receive personalised recommendations

### Administrators
Administrators can:
- import and manage book metadata from a public source
- maintain and correct stored metadata
- manage application content where required

## Data Sources
The system uses both internal and external data sources.

### Internal Data Source
A SQL database is used to store the main relational data, including:
- books
- authors
- reviews
- users
- reading list entries

For the current implementation:
- **SQLite** is used for local development and testing
- **PostgreSQL** is the intended production deployment database

### External Data Sources
The implemented public metadata source is:
- **Open Library**

The project includes a curated CSV dataset generated from the Open Library Search API and stored as `data/raw/open_library_books.csv`. This dataset is created by `scripts/fetch_open_library_dataset.py` and imported into the application database by `scripts/import_books_from_csv.py`.

This public metadata source is used to populate the local database with bibliographic details such as title, author, ISBN, publication year, genre, ratings average, and ratings count.

## Non-Functional Requirements
The project will also prioritise the following non-functional requirements:
- RESTful and consistent API design
- JWT-based authentication and access control
- clear and standardised error handling
- automatically generated API documentation
- deployment on an external hosting platform
- maintainable and testable code structure

## Exclusions
The following features are outside the scope of this project:
- a dedicated frontend website
- advanced social or community interaction features
- a fully trained machine learning recommendation model
- large-scale distributed or microservice-based infrastructure
- live third-party metadata enrichment at request time (e.g. direct runtime integration with Google Books)