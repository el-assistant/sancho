-- :name repo_exists :scalar
select id from git_repo where path=:repo_path;

-- :name create_repo :scalar
insert into git_repo(path,full_name) values (:repo_path, :repo_name) returning id;

-- :name file_exists :scalar
select id from files where repo_id=:repo_id and local_path=:local_path;

-- :name create_file :scalar
insert into files(local_path,repo_id) values ( :local_path, :repo_id) returning is;

-- :name create_node :insert
insert into ast_nodes (file_id, kind, parent_id, next_id, content) values (:file_id, :kind, :parent_id, :next_id, :content);
