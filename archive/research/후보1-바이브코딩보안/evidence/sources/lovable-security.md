> ## Documentation Index
> Fetch the complete documentation index at: https://docs.lovable.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Security overview

> Protect your apps with built-in security scans, API key protection, database access checks, dependency audits, and optional security integrations.

Lovable helps reduce common application security risks during development and before publishing. It does this in two main ways: by preventing common security mistakes up front, and by identifying potential vulnerabilities through automated analysis.

Lovable includes two built-in security scanners, **Basic scan** and **Deep scan**, plus optional connectors for additional coverage. These tools support secure application development, but they do not replace a thorough security review.

You are responsible for ensuring that your app meets the security requirements appropriate for its use case, especially if it handles sensitive data or performs critical functions.

<Warning>
  These tools help identify common security issues, but they cannot guarantee complete security. For apps handling sensitive data or critical functionality, consider an additional professional security review.
</Warning>

## Built-in security scanners

Lovable provides two built-in security scanners: **Basic scan** and **Deep scan**.

### Basic scan

The built-in **Basic scan** is a fast configuration and dependency check. It covers multiple areas, including:

* **RLS policy linting**: Checks row-level security policies for common mistakes
* **Database schema review**: Reviews database schema and access control
* **Dependency audit**: Detects known vulnerabilities in npm dependencies

### Deep scan

The built-in **Deep scan** performs a thorough agentic review of your codebase. A Deep scan runs everything the Basic scan does, and adds areas such as:

* **Access control review**: Detects overly permissive data-access rules and database functions that bypass row-level security
* **Backend endpoint protection**: Flags edge functions and APIs that lack proper authentication or authorization
* **Code-level vulnerabilities**: Identifies exposed secrets, unsafe input handling (such as SQL injection or XSS), insecure storage settings, and information leakage through errors or logs
* **Project-specific issues**: Surfaces issues tied to context you've added in your [security memory](#improving-scan-accuracy-with-security-memory)

<Tip>
  **Schedule security scans (Enterprise only)**

  Workspace admins and owners on Enterprise plans can schedule deep security scans to run automatically across all projects. See [Schedule security scans](/features/security-center#schedule-security-scans-enterprise-only) for more information.
</Tip>

## Optional security app connectors

Workspaces can also connect **optional security integrations** to extend coverage beyond Lovable’s built-in scanners.

### Wiz scanning

Workspaces can connect **Wiz** to add enterprise-grade vulnerability and code-security detection to every project in the workspace.

Wiz combines two analyses:

* **Software composition analysis (SCA)**: Identifies vulnerable dependencies, including transitive ones, using Wiz's continuously updated security database
* **Static application security testing (SAST)**: Scans your source code for risky patterns, hardcoded secrets, and unsafe API usage

Once a Wiz connection is added at the workspace level, Wiz scanning runs as part of Lovable's standard security scan suite. Findings appear in each project's Security view alongside results from the other scanners, in a section attributed to your Wiz connection.

See [Scan your projects for vulnerabilities with Wiz](/integrations/wiz) for setup and details.

### AI penetration testing with Aikido

The built-in scanners and Wiz perform **static analysis** by reading your code and configuration to flag patterns that look risky. AI penetration testing complements this with **dynamic analysis**: AI agents interact with your running application, send real payloads, and attempt to exploit authentication, authorization, and API flows like a real attacker would.

Workspaces can connect **Aikido** to run AI pentests on individual projects. Because pentests confirm each issue through a real attack scenario, every reported finding is exploitable rather than theoretical. Findings sync into the project's Security view in a dedicated **Agentic penetration test by Aikido** section, and Aikido also generates a shareable report structured for SOC 2, ISO 27001, and security questionnaires.

The recommended order is: run the security scanners first, fix what they surface, then validate with a pentest before a major release.

See [Run AI-powered penetration tests with Aikido](/integrations/aikido) for setup, prerequisites, and how to run pentests.

## When security scans run

Lovable runs security scans at different points in your workflow to help catch issues early.

Each scan runs only when it is relevant to your project and when changes have occurred since the last run. For example, database checks only run for projects with a connected database. The dependency audit runs automatically whenever your project's dependency files change, whether you edit them in Lovable or push the change to your synced Git repository. To refresh it at any other time, click **Scan dependencies** in the [project security view](/features/security-view).

<Note>
  The **Deep scan** does not run automatically as you work. You can run it from the [project security view](/features/security-view) or the [workspace security center](/features/security-center). The [publish dialog](/features/publish) offers it when the Basic scan finds critical issues.
</Note>

### Before publishing

When you open the [publish dialog](/features/publish), Lovable automatically runs the **basic security scan** in the background, including **RLS policy linting** and **database schema review**. The dialog shows the result on a single line. If the scan finds critical issues, the dialog shows the full findings and offers a **Deep scan** before you proceed.

Resolve all critical issues before making your app publicly available. Publishing with unresolved critical issues is possible, but strongly discouraged, especially for production apps or apps handling sensitive user data.

<Tip>
  **Publishing controls**

  Workspace admins and owners can enforce stricter publishing rules in **Workspace settings → Privacy & security** to help ensure insecure applications are never deployed. **Block publishing with critical issues** prevents publishing while error-level findings are unresolved.
</Tip>

### On demand

You can trigger a scan on demand from three places:

* [Project Security view](/features/security-view): on the **Code analysis** tab, click **Basic scan** to refresh the database and dependency checks, or **Deep scan** to run the full agentic code review (which also re-runs any out-of-date basic checks). Each button is disabled when its results are already up to date.
* [Workspace Security center](/features/security-center): click **Scan** on a project row. This runs every available scanner for that project (Basic and Deep together) in the background.
* [Publish dialog](/features/publish): the Basic scan kicks off automatically when the dialog opens, and the dialog shows the result on a single line. When the scan finds critical issues, the dialog shows the full findings and offers the **Deep scan** before publishing.

On-demand scans are useful after significant code changes, when investigating a specific finding, or when you want all results to reflect the current state of your project.

### Scheduled scans (Enterprise only)

Workspace admins and owners on Enterprise plans can schedule Deep security scans to run automatically across selected projects. Scheduled scans help keep projects covered without requiring admins to trigger scans manually.

See [Schedule security scans](/features/security-center#schedule-security-scans-enterprise-only) for setup details, available schedule options, and credit usage.

## How Lovable keeps your apps secure

The sections below explain the main areas of risk in more detail and how Lovable helps you address them.

For practical guidance on writing secure code and avoiding common security mistakes, see [Security best practices for Lovable apps](/tips-tricks/security-best-practices).

### Protecting API keys

Lovable generates frontend code that runs in the browser, which means API keys and other secrets cannot be stored safely in client-side code. Exposing credentials can lead to data leaks or unauthorized access.

To prevent sensitive credentials from being exposed, Lovable automatically detects API keys pasted into the project chat and guides you to store them securely in **Secrets** instead of hardcoding them into your code. When Lovable recognizes which tool the key belongs to, it also offers to set up a [connector](/integrations/introduction) for that tool. See [Secrets](/features/secrets) for how the key is stored in each case.

Rather than pasting credentials directly, describe what you want to build and Lovable will help you implement a secure setup using server-side functions and secret storage.

**For example:**

```text wrap theme={null}
I want to integrate service X API to generate text responses
```

Lovable will guide you to:

1. Store your API key securely in Secrets
2. Create an Edge Function to make the API call server-side
3. Call that Edge Function from your frontend code

This approach keeps credentials secure and follows web security best practices.

### Protecting data access with row-level security (RLS)

Row-level security (RLS) policies control which users can access or modify data in your database. Misconfigured RLS rules are a common cause of data leaks. You can review every policy in your project under **More → Cloud → Database → RLS policies**; see [RLS policies](/features/database#row-level-security-rls-policies).

Lovable helps you review and reason about your RLS policies to ensure users only see and change the data they are authorized to access. The Basic scan's **RLS policy linting** highlights overly permissive rules or missing access checks that could expose sensitive data. A Deep scan includes this check as well.

You should review RLS policies regularly, especially before publishing or after changes to authentication or database structure.

### Identifying database security risks

Database schemas and access rules work together to determine how data is exposed. Unsafe combinations of schema design and access policies can introduce security risks even when individual rules appear correct.

The Basic scan's **database schema review** examines your schema and RLS configuration together to identify patterns that could lead to unauthorized access or data exposure. This helps catch issues that may not be obvious when reviewing rules in isolation. The Deep scan includes this review and additionally performs an **access control review** that detects overly permissive data-access rules and database functions that bypass RLS.

### Identifying vulnerabilities in dependencies

Third-party libraries are a common source of security risk. Even widely used packages can introduce vulnerabilities when new issues are discovered.

The Basic scan's **dependency audit** checks your project's dependencies for known security vulnerabilities, identifies vulnerable packages, and provides information to help you assess and remediate the risk.

Dependency vulnerability findings may appear:

* In the project-level [Security view](/features/security-view), where you can review details and take action for a single project
* In the workspace-level [Security center](/features/security-center), where workspace admins and owners can monitor vulnerabilities across multiple projects

Findings include the affected package name and version, the type of vulnerability, and recommended remediation steps, such as updating to a secure version. Some critical vulnerabilities are not raised as findings: either Lovable has confirmed they cannot affect Lovable apps, or their [EPSS](https://www.first.org/epss/) score, an industry estimate of how likely a vulnerability is to be exploited, is low. These stay visible in the project's dependency list with a marker that explains why. See [Review project dependencies](/features/security-view#review-project-dependencies).

Keeping dependencies up to date is an important part of maintaining a secure application. When critical vulnerabilities are disclosed, the Security center can help identify which projects are affected so issues can be addressed quickly.

### Identifying vulnerabilities in application code

Application code can introduce security risks through patterns such as improper input handling, weak authorization checks, or exposed credentials. These are areas the Basic scan does not cover.

The [**Deep scan**](#deep-scan) analyzes your application code and database schema (in addition to running every basic check) to identify common vulnerability patterns and provide recommendations for improving security. These checks help surface issues early, before they become exploitable in production.

## Acting on security findings

After scans identify security findings, you can review and address them from the project-level Security view, through eligible automatic fixes, or through conversational security reviews.

### Review and fix findings in the project security view

For project-level findings, use the [Project security view](/features/security-view).

The Security view lets you inspect findings for a single project, understand severity, review suggested remediation steps, run scans, fix individual findings, use **Try to fix all**, ignore findings that do not apply, and review dependency vulnerabilities.

This is the primary place to work through scan results during development, before publishing, and after launch.

### Let Lovable automatically fix eligible findings

Lovable can automatically fix eligible security findings during regular agent work. When auto-fix is enabled, Lovable gets the latest **critical Basic scan findings**, marked as **error**, as part of its context whenever you chat with it. Lovable then attempts to resolve them as part of the next response. This is treated as standard build usage and consumes credits.

Auto-fix is designed for findings that are safe to remediate automatically, such as common row-level security (RLS) misconfigurations and database access patterns. It does not apply fixes for Deep scan findings.

Auto-fix is checked each time you send a message in the project chat:

1. You send any message in the project chat.
2. Lovable checks whether auto-fix is enabled for the project.
3. If enabled, Lovable gets the current list of eligible error-level Basic scan findings as additional knowledge.
4. Lovable attempts to fix those findings as part of what you asked for.

Auto-fix can be configured at two levels:

* **Workspace default**: Workspace admins and owners can set the default behavior across projects from **Workspace settings → Privacy & security → Security automation → Auto-fix security issues**.
* **Project setting**: Anyone with project edit access can manage auto-fix for a specific project from **Project settings → Auto-fix security issues**, unless the workspace default requires auto-fix for that project.

The available workspace options depend on your plan:

| Option                            | What it means                                                                                                                                                                                                                                                                                  |
| :-------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Selected project**              | Auto-fix is disabled by default. You can enable or disable it for individual projects from **Project settings → Auto-fix security issues**.                                                                                                                                                    |
| **Externally published projects** | Auto-fix runs automatically only after the project is published externally. After that, it runs each time you send a message in the project chat. You cannot disable it for externally published projects at the project level. You can still enable it manually for other projects.           |
| **All published projects**        | Auto-fix runs automatically only after the project is published, internally or externally. After that, it runs each time you send a message in the project chat. You cannot disable it for published projects at the project level. You can still enable it manually for unpublished projects. |
| **All projects**                  | Auto-fix runs automatically each time you send a message in the project chat of any project in the workspace, whether or not it has been published. It cannot be disabled at the project level.                                                                                                |

### Ask Lovable to review your app’s security

Separate from the automated security scanners, you can ask Lovable to perform a **conversational security review** at any time by prompting. This review is treated as standard build usage and consumes credits.

For example:

```text wrap theme={null}
Review my app's security
```

Lovable analyzes your project and responds with a detailed assessment. The review typically covers areas such as:

* Potential vulnerabilities in your application code
* Common issues like XSS risks, input handling, and authentication flaws
* Database schema and row-level security (RLS) policies
* Overall security posture with specific recommendations

The scope and depth of the review depends on your project. You can also ask Lovable to focus on a specific area, for example:

```text wrap theme={null}
Review the authentication flow in my app.
```

or

```text wrap theme={null}
Check if my API routes are secure.
```

Conversational reviews are especially useful after significant changes or before major releases. Even if no warnings are currently shown, periodically requesting a review is a good practice for production applications.

## Where to manage security

Lovable provides two security surfaces: one for securing individual projects and one for monitoring security across an entire workspace.

### Project security (Security view)

Use the [**Security view**](/features/security-view) when you are building or maintaining a specific project. It brings together findings from Lovable’s Basic scan and Deep scan, plus optional integrations such as Wiz and Aikido, so you can understand and address security risks in one place.

The Security view helps you:

* Run Basic scan and Deep scan on demand
* See whether scan results are up to date or need to be refreshed
* Review project findings by severity, including errors, warnings, and info
* Understand what each finding means, why it matters, and how to fix it
* Use security memory to give the scanner project-specific context and reduce false positives
* Fix individual findings, use **Try to fix all**, or make manual changes
* Ignore findings that do not apply, with a recorded reason
* Review project dependencies and known vulnerabilities
* Fix vulnerable packages in bulk and trigger a fresh dependency audit
* Download a JSON report of project dependencies and vulnerabilities
* Verify that your project is ready to publish
* Continue monitoring security after publishing as your project changes

This is the primary place to work through security issues for a single project during development, before publishing, and after launch.

### Workspace security (Security center)

Workspace admins and owners on Business and Enterprise plans can use the [**Security center**](/features/security-center) to monitor security across all projects in a workspace.

The Security center helps you:

* See which projects have errors, warnings, or outdated scan results
* Monitor scan coverage across the workspace, including projects that have never been scanned
* Run security scans for individual projects without opening them
* Schedule recurring deep security scans across the workspace, on Enterprise plans
* Review dependency vulnerabilities by project or by vulnerability
* Identify vulnerable packages that affect multiple projects
* View secrets across all projects without exposing secret values
* Find stale or duplicated secrets that may need cleanup
* Export security, dependency, and secrets data for audits or internal reporting
* Track overall security posture at the workspace level

The Security center also includes [**Security insights**](/features/security-insights), a portfolio-level view that combines security findings, ownership, lifecycle, publish status, and activity into a single **review priority** per project, so you can spot externally published projects, abandoned projects, projects with no owner, and projects with open security findings. On Enterprise plans, Security insights also incorporates sensitive data findings (PII), so you can also spot externally published projects that contain personal data.

The Security center aggregates security information across the workspace, but fixes are still applied at the project level.

## Show your app's security posture to others

Scans and fixes help you find and resolve issues while you build. To show customers, security reviewers, and investors what your app's security looks like from the outside, enable a [Trust center](/features/trust-center) for your externally published app: a page at `/.well-known/trust.html` on your app's own domain where Lovable publishes verifiable security facts it observes about the live app. Your app's code can't edit the results, and the page is informational, not a certification.

## Related security settings

In addition to project and workspace security reviews, Lovable provides account-level and authentication-related security settings. These configurations are not tied to a specific project, but they play an important role in protecting user accounts and reducing the risk of compromised credentials.

You should review these settings when setting up authentication or before launching an app that allows users to sign in.

### Leaked password protection

If your app uses email and password authentication, you can prevent users from choosing known compromised passwords.

This protection checks user passwords against the **HIBP (Have I Been Pwned) database** and rejects commonly leaked or easy-to-guess passwords. Enabling it helps reduce the risk of account takeovers caused by reused credentials.

* **Using the built-in backend (Cloud)**: Enable **Password HIBP check** in **More → Cloud → Users → Auth settings → Email**. See [Password rules](/features/email-auth#password-rules).
* **Using Supabase directly**: See the Supabase documentation on [Password strength and leaked password protection](https://supabase.com/docs/guides/auth/password-security#password-strength-and-leaked-password-protection) for detailed instructions.

## Costs and usage

Lovable includes both automated and conversational security tools. Most security features are free to use, while some security actions consume credits.

Automated and conversational security tools are designed to work together. Use automated security tools for continuous monitoring and targeted fixes during development and before publishing. Use conversational security reviews when you want a deeper, exploratory assessment of your app’s overall security posture.

### Automated security actions (free)

The following automated security actions do not count as standard build usage:

* **Running security scans**\
  Running **Basic scan** or **Deep scan** in the Security view, Security center, or publish dialog is free.
* **Fixing detected issues**\
  Fixing findings using **Try to fix all** in the Security view draws from your account's [10 free fixes](/features/projects/chat#fix-errors-and-get-unstuck), shared with **Try to fix** on build errors in all your workspaces and projects. Each free fix becomes available again 24 hours after you use it. Past the 10, further fixes are treated as standard build usage and consume credits.

These actions use Lovable's automated security scanners or security-specific remediation tools.

### Conversational security actions (uses credits)

The following conversational security actions are treated as standard build usage and consume credits:

* **Conversational security review**\
  Asking Lovable to “review my app’s security” in the project chat runs a conversational, AI-driven review that is treated as standard build usage and consumes credits.
* **General security questions in the project chat**\
  Asking security-related questions directly in the project chat, outside of automated security tools, is treated as standard build usage and consumes credits.
* **Referencing a finding in the project chat**\
  Referencing a security finding in the project chat to ask Lovable to analyze or fix it is treated as standard build usage and consumes credits.
* **Letting Lovable fix eligible findings during regular agent work**\
  [Letting Lovable fix eligible security findings during regular agent work](#let-lovable-automatically-fix-eligible-findings) is treated as standard build usage and consumes credits.

### Third-party integrations (separate costs)

Optional integrations involve third-party costs for scanning or testing. These costs are separate from Lovable credits.

* [Wiz scanning](/integrations/wiz) runs as part of Lovable’s standard security scan suite and does not consume Lovable credits. However, Wiz usage is governed by your Wiz deployment, including any Wiz quotas, limits, or charges.
* [AI pentests with Aikido](/integrations/aikido) are billed by Aikido and do not consume Lovable credits.

Fixing or discussing findings in Lovable follows the same credit rules as other security actions: automated security fixes draw from your account's [10 free fixes](/features/projects/chat#fix-errors-and-get-unstuck), while general chat-based security actions are treated as standard build usage and consume credits.


## Related topics

- [Workspace security center](/features/security-center.md)
- [Privacy & security settings](/features/privacy-and-security-settings.md)
- [Security best practices for Lovable apps](/tips-tricks/security-best-practices.md)
- [Project security view](/features/security-view.md)
- [Lovable for Enterprise](/introduction/lovable-for-enterprise.md)
