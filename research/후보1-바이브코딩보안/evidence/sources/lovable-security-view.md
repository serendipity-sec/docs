> ## Documentation Index
> Fetch the complete documentation index at: https://docs.lovable.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Project security view

> Review scan results, fix vulnerabilities, and manage dependency risks for a single project before and after publishing.

<head>
  <script type="application/ld+json">
    {`{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": "How do I access the Security view?", "acceptedAnswer": {"@type": "Answer", "text": "You’ll find the Security tab inside any Lovable project by going to More → Security in the project toolbar."}}, {"@type": "Question", "name": "What does outdated mean?", "acceptedAnswer": {"@type": "Answer", "text": "A scan's results are outdated when your project has changed since the last run. Click Basic scan or Deep scan to refresh results. Actions on outdated findings are disabled to prevent acting on stale information."}}, {"@type": "Question", "name": "What is the difference between Basic scan, Deep scan, and asking Lovable to review security?", "acceptedAnswer": {"@type": "Answer", "text": "Basic scan is a faster configuration and dependency check. It looks for common database issues and vulnerabilities in dependencies. Deep scan runs a more detailed agentic code review and usually takes longer. Both actions are free and do not consume credits. Asking Lovable to review your app's security in the project chat triggers a separate AI-driven review that provides a narrative report and recommendations. It does not update scan results or scan status. Conversational security reviews in the project chat consume credits. These approaches are complementary."}}, {"@type": "Question", "name": "Can I use the Security view for published projects?", "acceptedAnswer": {"@type": "Answer", "text": "Yes. Continue monitoring security after publishing, especially when adding features or updating dependencies."}}, {"@type": "Question", "name": "What happens if I publish with critical findings?", "acceptedAnswer": {"@type": "Answer", "text": "Lovable warns you before publishing if critical issues exist. You can choose to publish anyway, but this is strongly discouraged since critical findings typically represent exploitable vulnerabilities. If your workspace has Block publishing with critical issues enabled, you need to resolve the critical issues before you can publish."}}]}`}
  </script>
</head>

## What is the Security view?

The Security view shows security findings for a single project. It brings together results from Lovable's built-in security scanners and findings from optional security connectors, such as Wiz and Aikido, so that you can understand risks, take action, and verify that your project is ready to publish.

For details on how each scan works and when scans run, see [Security overview](/features/security).

You’ll find the **Security tab** inside any Lovable project by going to **More → Security** in the project toolbar.

<Tip>
  The Security view focuses on a single project.

  * To monitor security findings and dependency risks across multiple projects, use the [Security center](/features/security-center).
  * For a portfolio-level view that combines security findings, PII, ownership, lifecycle, and activity into a single review priority per project, see [Security insights](/features/security-insights).
  * To show customers and security reviewers verifiable facts about your externally published app, see the [Trust center](/features/trust-center). The Security view is where you find and fix issues. The Trust center is the outward-facing page Lovable generates from what it observes.
  * For practical guidance on writing secure code and avoiding common security mistakes, see [Security best practices for Lovable apps](/tips-tricks/security-best-practices).
</Tip>

## Why use the Security view?

* **Review all project security sources in one place**\
  Built-in scan results and optional connector findings appear together, so you do not need to check separate tools to understand a project’s security status.
* **Catch issues early**\
  Security issues are easier to fix during development than after deployment. The Security view helps identify common problems such as misconfigured database access, insecure code patterns, or vulnerable dependencies before your app goes live.
* **Focus on what matters**\
  Not all security findings carry the same risk. Findings are categorized by severity so you can prioritize critical issues first and review lower-risk recommendations later.
* **Save time with guided fixes**\
  Many findings include automated remediation options or clear guidance. You can ask Lovable to fix specific issues directly and review the resulting changes.
* **Track security as your project evolves**\
  As your project changes, previous scan results may become outdated. The Security view clearly shows when scans need to be refreshed so you always know your project’s current security state.

## Understanding scan status

The scan status at the top of the Security view shows whether your security results reflect your latest changes.

* **Up to date**: All scans reflect the current version of your project.
* **Out of date**: One or more scans have not run since the project changed.
* **Scanning**: Scans are currently running.

Scan results are tied to a specific version of your code. When your project changes, earlier results may no longer be accurate and are marked as outdated.

## Run Basic and Deep scans

Use the scan banner at the top of the Security view to run available scans and see the latest scan state. Depending on the current project state, you may see actions such as **Basic security scan** or **Deep security scan**.

The Basic scan is a faster configuration and dependency check, while the Deep scan runs a more detailed agentic code review. Both actions are free and do not consume credits.

<Note>
  The **Deep scan** does not run automatically as you work. You can run it from the [project security view](/features/security-view) or the [workspace security center](/features/security-center). The [publish dialog](/features/publish) offers it when the Basic scan finds critical issues.
</Note>

You should run scans:

* Before publishing
* After significant code or database changes
* When adding or updating dependencies
* Periodically for production applications

## Included security findings

The Security view brings together security findings for one project. Depending on your project setup and workspace integrations, it can include:

* **Basic scan findings**: Database and dependency findings from row-level security (RLS) policy linting, database schema review, and dependency audits.
* **Deep scan findings**: Agentic codebase review findings, including access control issues, unprotected backend endpoints, exposed secrets, unsafe input handling, and other code-level risks.
* **Wiz findings**: Static analysis and software composition analysis results from a connected [Wiz integration](/integrations/wiz), including vulnerable dependencies and risky code patterns.
* **Aikido findings**: Confirmed exploitable issues from AI penetration tests run through the [Aikido connector](/integrations/aikido).
* **Project dependencies**: A list of project `npm` dependencies with known issue counts by severity, a bulk fix action, and JSON export.

Findings are grouped by scanner and severity so you can understand where each issue came from, prioritize what matters, and decide whether to fix, ignore, or investigate further.

## Review and fix security findings

All findings appear under **Detected issues** and are grouped by **severity level**.

If the latest scan does not find anything, Lovable shows a **No issues found** state. This means the latest scan did not surface findings, but it does not guarantee that the project has no security risk.

If any errors exist, the view defaults to showing them first.

* **Error**: Critical problems that need your attention right away
* **Warning**: Issues you should review and fix if necessary
* **Info**: Suggestions to consider implementing

Click a finding to expand it and review full details, including:

* Which scan produced the finding
* A detailed explanation of the issue
* Why the issue matters for security
* Suggested remediation steps

You can address findings in several ways:

* **Fix a specific finding**\
  Reference a finding in the project chat to ask Lovable to analyze or fix that issue. This is treated as standard build usage and consumes credits.
* **Fix multiple findings at once**\
  Use **Try to fix all** to attempt automatic remediation for all findings in the current filter. It requires the **Deep scan** results to be up to date. Security fixes draw from your account's [10 free fixes](/features/projects/chat#fix-errors-and-get-unstuck), shared with **Try to fix** on build errors in all your workspaces and projects. Past the 10, further fixes are treated as standard build usage and consume credits.

Always review the changes Lovable makes and test them thoroughly.

If a finding does not apply to your use case, you can **ignore** it by providing a reason. Ignored findings remain visible, are marked with an ignored label, and can be restored at any time.

Ignoring findings should be a deliberate decision. If you are unsure whether a finding applies, ask Lovable for clarification before ignoring it.

Running scans in the Security view is free and does not count toward any limit. Automated fix actions draw from your account's [10 free fixes](/features/projects/chat#fix-errors-and-get-unstuck), shared with **Try to fix** on build errors in all your workspaces and projects. Each free fix becomes available again 24 hours after you use it, and further fixes are treated as standard build usage and consume credits. Conversational security reviews in the project chat, and referencing a finding in the project chat, consume credits. See [Security overview](/features/security) for details.

<Tip>
  **Let Lovable automatically fix eligible findings**

  Depending on your workspace and project settings, Lovable can automatically fix eligible **Basic scan** findings, such as common row-level security (RLS) and database access issues, during regular agent work. See [Let Lovable automatically fix eligible findings](/features/security#let-lovable-automatically-fix-eligible-findings) for how workspace and project settings interact, and which findings are eligible.
</Tip>

## Review project dependencies

The Security view shows a **Project dependencies** card with a count of project `npm` packages and known issues.

Click **Review** to open the dependency list. The list covers production dependencies (the packages your app uses when it runs) and leaves out development-only packages. Each row shows:

* Package name and version
* **Known issues** counts by severity, shown as badges such as **2 Critical** or **1 High**

Dependencies with known issues appear first, ordered by severity, followed by the remaining packages in alphabetical order.

If the list contains known issues, a **Try to fix all** button appears. Click it to send every dependency with known issues through a single fix request. Like other automated fix actions, it draws from your account's [10 free fixes](/features/projects/chat#fix-errors-and-get-unstuck).

You can also:

* Click **Scan dependencies** to refresh the dependency audit
* Click **Download list** to download a JSON report of all listed dependencies and their vulnerabilities for audits or compliance reviews

If the dependency list fails to load, the card shows an error state with a **Retry** button.

<Note>
  Some vulnerabilities rated critical upstream are not treated as findings, either because they cannot affect Lovable apps (such as a build-time dependency that never runs in your deployed app) or because they are very unlikely to be exploited in practice. For the second case, Lovable uses the [EPSS](https://www.first.org/epss/) score, an industry estimate of how likely a vulnerability is to be exploited, and does not raise a finding when that likelihood is low.

  Either way, the package stays in the dependency list with an info marker instead of a severity badge, and hovering the marker explains which reason applies. These packages don't count toward the Known issues total and are not included in **Try to fix all** requests, but their vulnerabilities still appear in the **Download list** export. The results refresh the next time a dependency scan runs, so click **Scan dependencies** to update an existing project, or wait for the next basic scan.
</Note>

Keeping dependencies up to date is one of the most effective ways to reduce security risk over time, especially as new vulnerabilities are disclosed.

## Improve scan accuracy with security memory

Click **Edit security memory** to open the security memory document for your project. This document is shared with the security scanner and Lovable agent and guides how it evaluates your project.

The document should cover the following:

* A short description of how your app works from an access control perspective. For example, whether it has authenticated users, what roles exist, or whether it handles sensitive data.
* What should never happen within your app's business logic. For example, users reading each other's private data, or unauthenticated access to admin actions.
* What not to create vulnerabilities for. This section is also updated when the agent accepts a risk during a scan. Each entry is one line explaining what risk is accepted. Do not use this section to dismiss legitimate security issues.

The security scanner reads this document before each scan and uses it to tailor recommendations and reduce false positives for your specific project. You do not need to fill in all sections immediately. Add context as you learn more about your app's security posture.

<Warning>
  Don't use the security memory to dismiss legitimate security issues. Focus on providing context about your app's purpose, users, and data sensitivity.
</Warning>

## Best practices for using the Security view

The Security view is designed for ongoing use throughout development, not just a final check before publishing. The following best practices reflect how builders commonly use it.

* **Keep security findings current**\
  Review findings regularly and refresh scans when results become outdated, especially after adding features, changing database access, or updating dependencies.
* **Prioritize critical issues**\
  Address error-level findings before warnings or informational items. Critical findings often represent exploitable vulnerabilities.
* **Use both scanning approaches**\
  Use the built-in Basic and Deep scans in the Security view for structured checks and targeted fixes. Complement them by periodically asking Lovable to “review my app’s security” in the project chat for a narrative analysis that may catch issues the automated scans miss. If your workspace uses Wiz or Aikido, review those connector findings alongside Lovable’s built-in scan results.
* **Manage dependency risk proactively**\
  Regularly review the dependency section and address high-severity vulnerabilities promptly.
* **Review and verify fixes**\
  Automated fixes can save time, but always review the changes and test your app before continuing development.
* **Be deliberate when ignoring findings**\
  Ignore findings only when they clearly do not apply. Revisit ignored findings as your project evolves.
* **Continue monitoring after publishing**\
  Publishing is not the end of security work. Monitor new findings as your app changes over time.

<Warning>
  Automated scans help catch common issues, but they cannot guarantee complete security. For apps handling sensitive data or critical functionality, consider an additional professional security review.
</Warning>

## FAQ

<AccordionGroup>
  <Accordion title="How do I access the Security view?">
    You’ll find the **Security tab** inside any Lovable project by going to **More → Security** in the project toolbar.
  </Accordion>

  <Accordion title="What does outdated mean?">
    A scan's results are outdated when your project has changed since the last run. Click **Basic scan** or **Deep scan** to refresh results. Actions on outdated findings are disabled to prevent acting on stale information.
  </Accordion>

  <Accordion title="What is the difference between Basic scan, Deep scan, and asking Lovable to review security?">
    **Basic scan** is a faster configuration and dependency check. It looks for common database issues and vulnerabilities in dependencies. **Deep scan** runs a more detailed agentic code review and usually takes longer. Both actions are free and do not consume credits.

    **Asking Lovable to review your app's security** in the project chat triggers a separate AI-driven review that provides a narrative report and recommendations. It does not update scan results or scan status. Conversational security reviews in the project chat consume credits.

    These approaches are complementary.
  </Accordion>

  <Accordion title="Can I use the Security view for published projects?">
    Yes. Continue monitoring security after publishing, especially when adding features or updating dependencies.
  </Accordion>

  <Accordion title="What happens if I publish with critical findings?">
    Lovable warns you before publishing if critical issues exist. You can choose to publish anyway, but this is strongly discouraged since critical findings typically represent exploitable vulnerabilities.

    <Note>
      If your workspace has **Block publishing with critical issues** enabled, you need to resolve the critical issues before you can publish.
    </Note>
  </Accordion>
</AccordionGroup>


## Related topics

- [Security overview](/features/security.md)
- [Workspace security center](/features/security-center.md)
- [Security best practices for Lovable apps](/tips-tricks/security-best-practices.md)
- [Lovable changelog](/changelog.md)
- [Publish your Lovable project](/features/publish.md)
