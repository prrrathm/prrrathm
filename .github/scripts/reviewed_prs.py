import requests
import os

GH_TOKEN = os.getenv("GH_TOKEN")
USERNAME = "prrrathm"

query = """
query ($login: String!) {
  user(login: $login) {
    pullRequests(first: 20, states: [CLOSED], orderBy: {field: UPDATED_AT, direction: DESC}) {
      nodes {
        title
        url
        author {
          login
        }
        reviews(first: 10) {
          nodes {
            author {
              login
            }
          }
        }
      }
    }
  }
}
"""

headers = {
    "Authorization": f"Bearer {GH_TOKEN}",
    "Content-Type": "application/json"
}

response = requests.post(
    "https://api.github.com/graphql",
    json={"query": query, "variables": {"login": USERNAME}},
    headers=headers
)

data = response.json()

prs = data["data"]["user"]["pullRequests"]["nodes"]
reviewed_by_me = [
    pr for pr in prs
    if any(review["author"]["login"] == USERNAME for review in pr["reviews"]["nodes"])
]

lines = ["## 👀 PRs Reviewed by Me\n"]

for pr in reviewed_by_me[:5]:  # Show top 5
    lines.append(f"- [{pr['title']}]({pr['url']})")

# Replace section in README
with open("README.md", "r") as file:
    content = file.read()

start = "## 👀 PRs Reviewed by Me"
end = "\n##" if "##" in content.split(start)[1] else ""
updated_section = "\n".join(lines)

if start in content:
    before = content.split(start)[0]
    after = content.split(start)[1]
    after = after.split(end, 1)[1] if end else ""
    new_content = before + updated_section + after
else:
    new_content = content + "\n\n" + updated_section

with open("README.md", "w") as file:
    file.write(new_content)
