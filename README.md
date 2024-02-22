# RMM WA Contact Archival Tool

The RMM WA Contact Archival Tool is a GitHub repository designed for automating the archival of contacts from Wild Apricot (WA) using GitHub Actions as a scheduled job (cron job). This tool facilitates archival of contacts so we can stay below our billing contact count without manual intervention (https://www.wildapricot.com/pricing).  

## Features

- **Automated Contact Archival**: Automatically archive contacts from Wild Apricot on a scheduled basis.
- **GitHub Actions Integration**: Utilizes GitHub Actions for scheduling and executing the archival process.
- **Configurable Schedule**: Customize the frequency of the archival process to meet specific needs.
- **Secure Authentication**: Implements secure handling of authentication credentials for accessing Wild Apricot's API.

## Getting Started

### Prerequisites

- A GitHub account.
- A Wild Apricot account with API access.
- Basic understanding of GitHub Actions and cron jobs.

### Setup Instructions

1. **Fork the Repository**
   
   Begin by forking this repository to your GitHub account. This creates a personal copy that you can customize and use.

2. **Configure Secrets**

   For secure authentication with Wild Apricot's API, you need to set up the following secrets in your GitHub repository settings:
   
   - `WA_API_KEY`: Your Wild Apricot API key.
   - `WA_ACCOUNT_ID`: Your Wild Apricot account ID.
   
   Navigate to your repository settings, then to `Secrets`, and add these secrets accordingly.

3. **Customize the Cron Schedule**

   The archival job is scheduled using a cron expression in the `.github/workflows/archival.yml` workflow file. Edit this file to set the schedule according to your needs.
   
   Example cron schedule for running the job every day at 2 AM UTC:
   ```yaml
   on:
     schedule:
       - cron: '0 2 * * *'
   ```

4. **Deploy the Workflow**

   Once the secrets are configured and the schedule is set, the workflow is ready to run automatically. You can also manually trigger the workflow to test the setup.

5. **Monitor Workflow Runs**

   Check the `Actions` tab in your GitHub repository to monitor the workflow runs and ensure the archival process is working as expected.

## Usage

Once configured, the RMM WA Contact Archival Tool runs automatically according to the specified schedule. Contacts from Wild Apricot will be archived and can be accessed in the specified output location (e.g., a dedicated branch or directory within the repository).

## Contributing

Contributions to the RMM WA Contact Archival Tool are welcome. Please follow the standard GitHub fork and pull request workflow to submit your contributions.

## Support

If you encounter any issues or have questions regarding the tool, please file an issue in the GitHub repository.

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file in the repository for full details.
