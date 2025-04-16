# 🚀 CostEstimator for OpenAI with tqdm integration 💸

The `CostEstimator` class offers a convenient way to estimate the cost of using OpenAI's gpt-3.5 and gpt-4 models. It is intended to be used in a loop with `tqdm` to  track and display the cost estimation in real-time.

## 🌟 Features:

![Screenshot of an estimation](https://raw.githubusercontent.com/michaelachmann/gpt-cost-estimator/master/images/screenshot.png)

- **tqdm Integration**: Seamlessly integrates into `tqdm` powered loops and displays the cost of each API call and the accumulated total cost.
- **Model Synonyms**: Easily switch between model versions or names. 🔄
- **Mock Responses**: Generate fake 🤖 API responses to estimate costs without making actual API requests.
- **Cost Breakdown**: Display the estimated 💰 cost per request and the accumulated cost.


## 🛠 Usage:
The CostEstimator class was designed to be used in Jupyter Notebooks, see the [example notebook](https://github.com/michaelachmann/gpt-cost-estimator/blob/master/examples/example_notebook.ipynb) for a demonstration. 

1. **Decorate your API call function**:
   ```python
   import openai 
   from gpt_cost_estimator import CostEstimator
   
   @CostEstimator()
   def query_openai(model, messages, **kwargs):
       args_to_remove = ['mock', 'completion_tokens']
   
       for arg in args_to_remove:
         if arg in kwargs:
             del kwargs[arg]
   
       return openai.ChatCompletion.create(
           model = model,
           messages = messages,
           **kwargs)
    ```

2. **Call the API from within a loop**:
    ```python
    for message in tqdm(messages):
        response = query_openai(model="gpt-3.5-turbo-0613", messages=[message], mock=False)
   
        # Or if you're mocking the API call:
        response = query_openai(model="gpt-3.5-turbo-0613", messages=[message], mock=True)     
   
    print() # We need to print a newline to show the total cost
    ```

3. **Reset Total Cost**:
    ```python
    CostEstimator.reset()
    ```

4. **Read Total Cost**:
    ```python
    CostEstimator.get_total_cost()
    ```

## 📌 Dependencies:

- `tiktoken`: Used to determine the number of tokens in a string without making an API call.
- `openai`: Official OpenAI Python client.
- `tqdm`: Provides the real-time progress bar that displays the cost details. Essential for user-friendly cost tracking.
- `lorem_text`: Generates mock API responses.

## 🔧 Installation:

**Install via pip**

```bash
pip install gpt-cost-estimator
```

**Manual Installation**

```bash
pip install tiktoken openai tqdm lorem_text
```
Clone this repository and import the `CostEstimator` in your script.

## How tqdm is Integrated:

The progress bar powered by `tqdm` provides instant feedback for every API call. Whether you're mocking the call or connecting to the real API, you'll see the cost of the current request and the total expenditure so far. It offers a visual and user-friendly way to monitor costs.

## 📝 Notes:

- Ensure the pricing details in the estimator match OpenAI's official pricing.
- Always test the estimator with your specific use cases to ensure accuracy.
- The progress bar will appear in your Jupyter notebook or console where the script runs.

## Change Log:
- 2024-01-26 Updated prices and added additional models.

## 📜 License:

The MIT License is a permissive open-source license. It allows for reuse of code with minimal restrictions, while requiring only attribution and inclusion of the original license. 🔄🔓💼