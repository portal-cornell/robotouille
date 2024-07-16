# Prompt Description

## 1.0.0

### Metadata

**version** stands for the prompt parsing version. This should match the above version; see the `docs` for other versions.

**experiment_name** is the name of the experiment this prompt belongs to

**prompt_description** is a short name to act as a memorable callback to the changes in this prompt

**prompt_version** is a versioning for the prompt, e.g. 1.2.3. It is recommended to use the first number for major changes, the second number for minor changes, and the third number for bug fixes.

### Prompt Data

**system** is for the system message

**instructions** is for the context message

**examples** are for few-shot examples (leave blank for zero-shot). Within **examples** can be
- **description** which is for YAML readability; explain what this example is for 
- **observation** which is the user input
- **response** which is the assistant or LLM response