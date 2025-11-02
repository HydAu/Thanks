# Assuming Python with Flask and PyGithub

# 1. Set up your Flask app to listen for webhook events
@app.route('/webhook', methods=['POST'])
def github_webhook():
    payload = request.json
    
    # 2. Verify webhook signature (IMPORTANT for security!)
    # You'll get a secret from GitHub when setting up the webhook
    if not verify_signature(request.data, request.headers.get('X-Hub-Signature-256')):
        return "Invalid signature", 403

    event_type = request.headers.get('X-GitHub-Event')

    if event_type == 'pull_request':
        handle_pull_request(payload)
    elif event_type == 'issues':
        handle_issue(payload)
    
    return "OK", 200

def handle_pull_request(payload):
    action = payload.get('action')
    pr = payload.get('pull_request')
    repo_name = payload.get('repository', {}).get('full_name')
    pr_number = pr.get('number')
    pr_state = pr.get('state') # 'open', 'closed'
    pr_merged = pr.get('merged') # True/False

    if action == 'closed' and pr_merged:
        contributor_login = pr.get('user', {}).get('login')
        message = f"🎉 Thank you, @{contributor_login}, for your excellent contribution! Your pull request has been successfully merged. We appreciate your hard work! 🎉"
        post_comment(repo_name, pr_number, message, 'pr')

def handle_issue(payload):
    action = payload.get('action')
    issue = payload.get('issue')
    repo_name = payload.get('repository', {}).get('full_name')
    issue_number = issue.get('number')
    issue_state = issue.get('state') # 'open', 'closed'

    if action == 'closed' and issue_state == 'closed':
        # You might want to check if someone actually contributed, 
        # or just thank the person who closed it if it was their work.
        # For simplicity, let's thank the person who created the issue or the last commenter.
        # More advanced bots might look at who made the last commit that closed it.
        creator_login = issue.get('user', {}).get('login')
        message = f"✨ Thank you, @{creator_login}, for your contribution/report! This issue has been successfully closed. We appreciate your help! ✨"
        post_comment(repo_name, issue_number, message, 'issue')


def post_comment(repo_full_name, item_number, message, item_type):
    # Initialize GitHub API client
    g = Github(os.environ.get('GITHUB_TOKEN')) # GITHUB_TOKEN should be set as an environment variable
    repo = g.get_user().get_repo(repo_full_name)

    if item_type == 'pr':
        item = repo.get_pull(item_number)
    else: # item_type == 'issue'
        item = repo.get_issue(item_number)
        
    # Optional: Check if the bot has already commented to avoid spam
    # comments = item.get_comments()
    # for comment in comments:
    #     if comment.user.login == 'your-bot-username':
    #         # Bot already commented, skip
    #         return

    item.create_comment(message)
    print(f"Commented on {item_type} #{item_number} in {repo_full_name}")

# You'll need to define `verify_signature` based on your language/framework
# and handle environment variables for your GitHub Token.
