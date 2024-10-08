## Evaluating Large Language Models

Current offline evaluation of large language models is an extremely complex and nuanced task, compounded by the speed of model development, continuously increasing options for evaluation metrics and their implementation, as well as lack of community consensus around metrics and pipelines.

When we perform evaluation for machine learning models, there are two modes, each of which seek to answer the question: "is the model we trained good enough to generalize beyond its training data for the machine learning task we want it to perform?"

+ **Offline evaluation:** We train a model and, using a holdout test set from our training data, we evaluate on metrics like precision, accuracy, recall, NCDG, RMSE from "classical" machine learning and BLEU and ROUGE for large language models, as relevant for our machine learning domain. The essential question we are trying to answer is: "given the ground truth in your test data, how well does the trained model make predictions?" The closer the match, the better it is.
+ **Online evaluation:** We ship the model to production as a customer-facing application or feature, (i.e. ChatGPT or Bard) and have people use it and give implicit or explicit feedback on whether the results were good. This could involve looking at user activity or text input/output in the application where we deploy our model. The essential question we are trying to answer is: "Given the live model, how good do people think it is?" The more people use it or the more relevant the results, the better the model actually is. Because offline and online scores don’t always match, it’s important to assess whether offline metrics are good proxies for online performance.

In "traditional" machine learning, particularly in class-based supervised learning tasks, evaluation is quite straightforward: if we have a model that predicts, based on someone’s X-rays, whether they have lung cancer, we can collect x-rays that have already been classified by doctors and see if the model we learned predicts the same class (YES/NO) for those samples.

In problems like recommendations and information retrieval ranking, which gets closer to the domain of LLMs, this gets harder. How do we know a "relevant" result was returned? Usually online ranking is the best fit here, but offline metrics like NDCG are considered good offline proxy metrics. They offer the ability to compare a returned recommendation/search prediction to a relevance judgment list and calculate the difference both in elements served and position of those elements, given the narrow confines of a specific task.

Taking this to the next level, what if we have a model that completes an endless number of different machine learning tasks: summarization, autocompletion, reasoning, generating recommendations for movies and recipes, writing essays, telling stories, translating documents, generating good code, and on and on? Evaluation becomes much harder, almost as hard as deciding if a real person will consistently give you trustworthy information.

## Evaluating Summarization

Finding a good model for summarization is a daunting task, as the typical intuition that larger parameter models generally perform better goes out the window. For summarization, we need to consider the input, which will likely be of a longer context size, and finding models that efficiently deal with those longer contexts is of paramount importance. In our business case, which is to create summaries of conversation threads, much as you might see in Slack or an email chain, the models need to be able to extract key information from those threads while still being able to accept a large context window to capture the entire conversation history.

We identified that it is far more valuable to conduct abstractive summaries, or summaries that identify important sections in the text and generate highlights,  rather than extractive ones, which pick a subset of sentences and add them together for our use cases since the final interface will be natural language. We want the summary results not to need to be interpreted from often incoherent text snippets produced by extractive summaries.

The most difficult part is identifying the evaluation metrics useful for judging the quality of summaries. Evaluation is a broad and complex topic, and it’s difficult to have a single metric that can answer the question: "is this model a good abstractive summarizer?"

For our early exploration, we stuck to tried-and-true metrics, limiting our scope to metrics that can be used with ground truth. Ground truth for summarization includes documents that are either manually summarized or bootstrapped from summaries generated by models and approved by humans.

These include:

    + ROUGE - (Recall-Oriented Understudy for Gisting Evaluation), which compares an automatically-generated summary to one generated by a machine learning model on a score of 0 to 1 in a range of metrics comparing statistical similarity of two texts.
    + METEOR - Looks at the harmonic mean of precision and recall
    + BERTScore - Generates embeddings of ground truth input and model output and compares their cosine similarity
