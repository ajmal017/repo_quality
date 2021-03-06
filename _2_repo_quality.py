import json, os, re, getpass, glob, time, datetime, traceback, sys

import requests, arrow, flask

import config, _1_repo_util, _0_hit_api

if not os.path.exists(config.cache_dir_path):
  os.mkdir(config.cache_dir_path)

class g:
  search_reset_time = None

def pull_paths(paths, auth=config.auth_, ignore_cache=False):
  mean_stars_per_issue = _1_repo_util.get_mean_stars_per_issue()
  repo_dicts = []
  min_score, max_score = None, None
  stars_per_issue_list = []
  for path in paths:
    try:
      repo_dict = pull_repo(path, mean_stars_per_issue, auth=auth, ignore_cache=ignore_cache)
      if min_score is None or repo_dict['score'] < min_score:
        min_score = repo_dict['score']
      if max_score is None or repo_dict['score'] > max_score:
        max_score = repo_dict['score']
      stars_per_issue = (
        float(repo_dict['stargazers_count'] / repo_dict['issue_count'])
        if repo_dict['issue_count'] != 0 else repo_dict['stargazers_count'])
      stars_per_issue_list.append(stars_per_issue)
      if not repo_dict:
        print 'null repo:', path, repo_dict
      repo_dicts.append(repo_dict)
      repo_dicts.sort(key=lambda d: -d['score'])
      repo_dicts = repo_dicts[:100]
    except Exception as e:
      print 'error reading:', path
      print (u'exception: {}; {}'.format(type(e).__name__, e.message)).encode('utf8')
      traceback.print_exc()
    except:
      print "Unexpected error:", sys.exc_info()[0]
      raise

  for repo_dict in sorted(repo_dicts, key=lambda d: -d['score']):
    print '        path:', repo_dict['path']
    print '       stars:', repo_dict['stargazers_count']
    print '      issues:', repo_dict['open_issues_count']
    print '  has_issues:', repo_dict['has_issues']
    print '         age:', repo_dict['age']
    print 'stars/issues:', repo_dict['stargazers_count'] / (repo_dict['open_issues_count'] or 1)
    print '   stars/age:', repo_dict['stargazers_count'] / (repo_dict['age'].days or 1)
    print '       score:', repo_dict['score']
    print

  printed_suck_line = False
  for repo_dict in sorted(repo_dicts, key=lambda d: -d['score']):
    if repo_dict['score'] < 180 and not printed_suck_line:
      printed_suck_line = True
      print '-------  suck line -------'
    print repo_dict['path']
    print ' ', repo_dict['score']


class SearchAPI:
  def __init__(self):
    self.rate_limit, self.reset_time = None, None

  def can_use(self):
    return self.rate_limit is None or self.rate_limit > 0 or time.time() > self.reset_time

search_api = SearchAPI()
def pull_repo(repo_path, mean_stars_per_issue, auth=None, priority=False, ignore_cache=False):
  _1_repo_util.validate_path(repo_path)
  cache_file_path = os.path.join(config.cache_dir_path, repo_path.replace('/', '_') + '.txt')

  def hit_api(repo_path, auth, suffix=''):
    return _0_hit_api.hit_api(repo_path, auth, suffix, priority_request=priority)

  if not os.path.exists(cache_file_path) or ignore_cache:
    print 'pulling info:', cache_file_path
    repo_dict = json.loads(hit_api(repo_path, auth))

    commits = json.loads(hit_api(repo_path, auth, '/commits'))
    primary_author = None
    if commits:
      author_to_count = {}
      for i, commit in enumerate(commits):
        if not commit['author']:
          continue
        author = commit['author']['login']
        author_to_count.setdefault(author, 0)
        author_to_count[author] += 1
      primary_author = max(author_to_count.items(), key=lambda t: t[1])[0]

    pulls = []
    for page in range(1, 100):
      page_str = hit_api(
        repo_path,
        auth,
        '/pulls?page={}'.format(page),
      )
      page_list = json.loads(page_str)
      if not page_list:
        break
      pulls += page_list

    repo_dict['pull_count'] = len(pulls)

    issues = json.loads(hit_api(repo_path, auth, '/issues'))
    self_issue_count = 0
    for issue in issues:
      if "pull_request" in issue:
        continue
      if issue['user']['login'] == primary_author:
        self_issue_count += 1
    repo_dict['self_issue_count'] = self_issue_count

    _1_repo_util.write_repo(repo_dict, mean_stars_per_issue, repo_path)

  with open(cache_file_path) as f:
    json_str = f.read()
  repo_dict = json.loads(json_str)

  # Redirect to new repo
  if repo_dict.get('path') != repo_dict.get('full_name'):
    return pull_repo(repo_dict.get('full_name'), mean_stars_per_issue, auth, ignore_cache)

  # Set default values for keys I recently added to db (and therefore might be missing).
  repo_dict.setdefault('path', repo_path)
  if 'age' in repo_dict:
    repo_dict['age'] = datetime.timedelta(seconds=repo_dict['age'])
  else:
    repo_dict['age'] = arrow.now() - arrow.get(repo_dict['created_at'])
  if not 'score' in repo_dict:
    _1_repo_util.rate_repo(repo_dict, mean_stars_per_issue)

  return repo_dict

if __name__ == '__main__':
  paths = []
  for cache_file_path in glob.glob(os.path.join(config.cache_dir_path, '*.txt')):
    with open(cache_file_path) as f:
      repo_dict = json.loads(f.read())
    paths.append(repo_dict['full_name'])
  pull_paths(paths, auth=None, ignore_cache=True)


  # pull_paths([
  #   # libs that have worked well
  #   'twbs/bootstrap', 'kennethreitz/requests', 'jasmine/jasmine', 'rails/rails',
  #   'angular/angular.js', 'tax/python-requests-aws', 'django/django', 'mitsuhiko/flask',
  #   'npm/npm', 'asweigart/pyperclip', 'JesseAldridge/github_quality', 'fabric/fabric',

  #   # libs I haven't tried much
  #   'Microsoft/TypeScript', 'meteor/meteor', 'facebook/react', 'angular/angular',
  #   'strongloop/express', 'dscape/nano', 'Level/levelup', 'felixge/node-mysql',
  #   'mongodb/node-mongodb-native', 'brianc/node-postgres', 'NodeRedis/node_redis',
  #   'mapbox/node-sqlite3', 'mafintosh/mongojs', 'tornadoweb/tornado', 'gevent/gevent',
  #   'percolatestudio/meteor-migrations', 'Polymer/polymer', 'Automattic/mongoose',
  #   'nodejs/node', 'sequelize/sequelize', 'Automattic/monk', 'balderdashy/waterline',
  #   'balderdashy/sails', 'playframework/playframework', 'pyinvoke/invoke',
  #   'msanders/snipmate.vim',

  #   # libs that have given me trouble
  #   'sindresorhus/atom-jshint', 'angular-ui-tree/angular-ui-tree',
  #   'boto/boto', 'rupa/z', 'lsegal/atom-runner'
  # ])
