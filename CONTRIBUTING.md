# Contributing

Lumigator is still in early stages of development and as such will have large variance between even PATCH versions in terms of feature development. Check the release notes to see what changed in between releases.

To stay updated on the latest announcements, also join our Discord channel: [Discord Channel](https://discord.com/channels/1089876418936180786/1281660143251095634).

We want to encourage both suggestions and contributions from the community in the near future. Before submitting a [pull request](https://github.com/mozilla-ai/lumigator/pulls), please open a discussion in a [related issue](https://github.com/mozilla-ai/lumigator/issues).

**Before you contribute**

* Check out the [roadmap](https://github.com/orgs/mozilla-ai/projects/17): This will give you an overview of the project's direction and help you identify areas where your contributions can have the greatest impact.
* Take a look into the existing issues: Check if your issue or challenge has already been discussed or reported. This helps avoid duplication of effort.
* Learn about the code: The Lumigator project consists of several packages, each with its own pyproject.toml file. Understanding the project structure will make it easier to contribute effectively: the `lumigator/python/mzai/backend` package that powers the lumigator server functionality, the `lumigator/python/mzai/schemas` package containing the formal schemas for communication with the server through the REST API, and the `lumigator/python/mzai/sdk` package abstracting the REST API for Python applications. Each package holds its own `pyproject.toml` definition.

### **Disclaimer**

We appreciate all contributions and are eager to review them. However, please understand that we may not be able to accept every contribution due to factors such as team capacity, project priorities, and the overall scope of the project.

We will carefully consider all submissions and provide feedback whenever possible. If your contribution is not accepted, please don't be discouraged! We value your input and appreciate you taking the time to contribute.

## **How Can I Contribute?**

**Reporting Bugs**

If you find an error while running Lumigator, we would appreciate you opening an [issue](https://github.com/mozilla-ai/lumigator/issues) to report it. Follow the corresponding template in Github providing a description of the bug, a detailed description on how to reproduce the reported behavior, a detailed description on what you would expect to happen and your system info. 

**Suggesting features**

If you have ideas for improvements or new features, feel free to open a new discussion or issue to share them. We appreciate well documented ideas or  suggestions. Clearly explain the problem you're trying to solve, the proposed solution, and any relevant diagrams or examples. You can also have at look to our ROADMAP to check if your proposal is aligned with the defined direction of the Lumigator.

We initiate a [discussion](https://github.com/mozilla-ai/lumigator/discussions) on GitHub to refine the implementation details. Once clarified, the feature can be implemented by either us or the reporter.

**Writing Code**

If you don’t know where to start, there is a special [Good First Issue](https://github.com/mozilla-ai/lumigator/contribute) page. It will give you a list of open issues that are beginner friendly and help you start contributing to our project. 

To contribute to Lumigator, first identify a need for a new feature or bug fix. Search existing issues and the roadmap to see if it's already been addressed. If not, we will follow the next process.

1. **Proposal**. The Github user ("User") open a github [issue](https://github.com/mozilla-ai/lumigator/issues), referencing the [roadmap](https://github.com/orgs/mozilla-ai/projects/17), and provides a clear description, including the problem, desired outcome, quick diagram and any relevant information.
2. **Issue triage**. Any Lumigator maintainer triages it, reviewing that the issue comes with enough details, and assigns labels (e.g., "bug", "enhancement", "help wanted") for better organization. If the issue has been correctly provided, the maintainer will asks other 2-3 folks for feedback and to assess the feasibility and priority of the issue.
3. **Discussion and refinement**. User is invited to open a [discussion](https://github.com/mozilla-ai/lumigator/discussions) to flesh out their idea with team.
4. **Contribute to the implementation**. Once the the issue is refined, the “User” is asked if they want to take it, otherwise it will enter into our internal prioritization process and we will keep you posted. The issue is updated with next steps (e.g. dropped / user or someone else implements independently / Lumigator team adds it into our backlog).
5.  **Implementation**
    - Fork the [repository](https://github.com/mozilla-ai/lumigator/).
    - Create a new branch for your specific contribution (name your branch using the github issue number and the issue's name)
    - **Coding and Test:** Make the necessary code changes, write unit tests to verify the correctness of your changes and include the documentation.
    - Create a pull request on GitHub, linking it to the original issue. Clearly describe the changes you've made and their impact.
6. **Code review and feedback.** The maintainers team will review the pull request, providing feedback and suggestions for improvement. We expect the “User” to address the feedback, making the necessary revisions to your code based. Once the code is reviewed and approved, the pull request will be merged into the main branch.
7. **Release.** Once merge, your code will be generally available in our repository as part of Lumigator.


## Where to go

* [Lumigator documentation](https://mozilla-ai.github.io/lumigator/): Describes all the components and includes usage guides.
* [Open issues](https://github.com/mozilla-ai/lumigator/issues): Browse the open issues to check if the topic you want to raise is already being discussed.
* [Contribute](https://github.com/mozilla-ai/lumigator/contribute): Explore the list of "good first issues" to start contributing.


