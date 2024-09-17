# Weaviate Workshop: Open Source Summit 2024

README for Open Source Summit 2024 Tutorial: "Build AI-Supercharged RAG Apps with a Vector Database"

# Step 1: Preparation & Setup

Clone this repo and navigate into it. This will be your working directory for the workshop.

```shell
git clone git@github.com:weaviate-tutorials/workshop-oss-2024.git
cd workshop-oss-2024
```

## 1.1 Install Python & set up a virtual environment

> [!NOTE]
> If you have a preferred setup (e.g. Conda/Poetry), please feel free to use that. Otherwise, we recommend following these steps.

Install `Python 3.9` or higher (e.g. from the [Python website](https://python.org/), or `pyenv`).

Then, create & activate a virtual environment:

```shell
python -m venv .venv  # Or use `python3` if `python` is Python 2
source .venv/bin/activate
```

Check that you are using the correct Python:

```shell
which python
```

This should point to the Python binary in the `.venv` directory.

Install the required Python packages:

```shell
pip install -r requirements.txt
```

> [!TIP]
> If you have network connectivity issues, the installation may time out part way through. If this happens, just try running the command again. It will re-used cached data, so you will make further

> [!TIP]
> If you open new terminal or shell window, you will need to activate the virtual environment again. Navigate to the project directory and run `source .venv/bin/activate`.

## 1.2 Set up Ollama

The workshop is set up for Ollama as the embedding & LLM provider. Note that Weaviate allows you to use one of many other model providers, such as Cohere or OpenAI. See our [model provider documentation](https://weaviate.io/developers/weaviate/model-providers) for more information.

We provide helper CLI to download the data & prepare your project for you:

> [!NOTE]
> - We will use pre-embedded data for this workshop, so Ollama will be used for vectorizing queries & LLM use
> - No account or API key required

Download & install Ollama from the [Ollama website](https://ollama.com/). Make sure Ollama is running, by:

```shell
ollama -v
```

You should see something like:
```shell
❯ ollama -v
ollama version is 0.3.8
```

Then, run the following command:

```shell
python workshop_setup.py
```

This will download the data file, and get Ollama to load the pre-configured models for the workshop (`nomic-embed-text` and `gemma2:2b`). This will take a few minutes.

If you have previously downloaded the data file, it will use a cached version. To overwrite the file, specify this flag::

```shell
python workshop_setup.py --use-cache False
```

> [!TIP]
> If the download is going to take *very* long (e.g. more than 10 minutes), maybe stop the download & use a smaller dataset. Do this by adding `--dataset-size 10000` to the end of your command, like:
>
> ```shell
> python workshop_setup.py --dataset-size 10000
> ```

While the download is progressing, you can continue to [the next section (1.3)](#13-install-containerization-tools). Leave the download running in the background.

## 1.3 Install Docker

Install Docker Desktop: https://www.docker.com/products/docker-desktop/

## 1.4 Install Go

The Streamlit app runs a Go command to get the Weaviate memory profile. You will need to have Go installed to run this command.

Install Go from the [Go website](https://golang.org/).

# Part 2: Cluster setup

Start up a (single-node) Weaviate cluster with the following command:

```shell
docker-compose up -d
```

This will start a single-node Weaviate cluster.

Check an Weaviate endpoint:

```shell
curl http://localhost:8080/v1/meta | jq
```

You should see a response - this means Weaviate is running!

You should also be able to see the memory usage of the Weaviate pod by running:

```shell
go tool pprof -top http://localhost:6060/debug/pprof/heap
```

This isn't necessary, but for the workshop, we'll give you an idea of how the memory usage changes as we add data to the system.

# Step 3: Work with Weaviate

In the in-person workshop, we will go through the introductory materials in `intro_workshop.ipynb` together. If you are doing this workshop on your own, you can go through the materials at your own pace.

For complete examples, see `intro_workshop_finished.ipynb` notebook.

## 3.1 Run the demo Streamlit app

We have a Streamlit app that will help you to visualise basic cluster statistics, and to do some cool things with the data. (Remember to navigate to the project directory and activate the virtual environment.) Run it with:

```shell
streamlit run app.py
```

This will throw an error, but that's OK. We'll fix that in the next step.

## 3.2 Use Weaviate

Now, let's load some data into Weaviate. You should now have these files:

1_create_collection.py
2_add_data_with_vectors.py

Run the first script to create a collection:

```shell
python 1_create_collection.py
```

We will take a look together at the script.

But if you would like, review it to see what it does. See what settings are being configured, and explore what options are available (or commented out - as alternatives).

Now, refresh your streamlit app from the browser. The app should no longer throw an error.

So let's run the second script to add data to the collection:

```shell
python 2_add_data_with_vectors.py
```

This should take just a few **seconds** to run. (We'll talk more about this, but that's because we're using pre-vectorized data.)

You should see the memory profile of the Weaviate pod increase as the data is added.

Now, refresh the Streamlit app. You should see the data in the app. Explore the app, and see what types of results you get for different search queries.

# Step 3.3

*************************
ENJOY THE WORKSHOP
*************************

# Step 4: Additional exercises to try

## 4.1 Update the vector index & quantization settings

In `1_create_collection.py`, you can change the settings for the vector index and quantization.

Notice the commented out lines for `quantization`. Try each one, and see how it affects the memory usage. Do you notice changes to the search results? Would you expect it to?

Try changing `.hnsw` to `.flat`. How does this affect the memory usage and the search performance of the system?
- Note: The `.flat` index can only be used with the `bq` quantization.

## 4.2 Try a larger dataset

If you want to experiment with even larger (or smaller) datasets, you can run the following command:

```shell
python workshop_setup.py --dataset-size <SIZE>
```

Where `<SIZE>` is one of `10000`, `50000` (default), `100000` or `200000`.

They are pre-vectorized datasets, so you can experiment with different sizes without having to wait for the data to be vectorized, or spend money on the inference.

## Finish up

When finished with the workshop, you can stop the cluster with:

```shell
docker-compose down
```
