# Project Scope

## Project Title
**Book Metadata, Review & Insight API**

## Overview
This project aims to design and implement a data-driven Web API for book metadata management, user reviews, reading list tracking, and analytical insights. In addition to standard CRUD functionality, the system will support metadata enrichment from external public sources and provide personalised recommendations based on user activity and stored review data.

## Objectives
The main objectives of the project are to:
- provide a structured RESTful API for managing books and related entities
- allow users to create, view, update, and manage book reviews
- support personal reading list management
- enrich locally stored book records using external public metadata sources
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
- import and enrich book metadata from external sources
- maintain and correct stored metadata
- manage application content where required

## Data Sources
The system uses both internal and external data sources.

### Internal Data Source
A local PostgreSQL database will be used to store the main relational data, including:
- books
- authors
- reviews
- users
- reading list entries

### External Data Sources
To improve metadata quality and coverage, the API will integrate:
- Google Books
- Open Library

These services will be used to enrich local records with bibliographic details such as ISBNs, categories, descriptions, author information, and cover images.

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