:- module(opencloud_editor,
	[ cloud_unload_user_package/1,
	  cloud_load_user_package/1,
	  cloud_unload_directory/1,
	  cloud_load_directory/1,
	  cloud_unload_file/1,
	  cloud_consult/1,
	  cloud_consult_string(+,t),
	  cloud_retract(+)
	]).

:- dynamic cloud_user_term/2.

is_prolog_source_file(_File) :- true.

%%
% Retract all PL files in a ROS package.
%
cloud_unload_user_package(PkgName) :-
  ros_package_path(PkgName,PkgPath),
  atom_concat(PkgPath,'/prolog',PrologDir),
  cloud_unload_directory(PrologDir).

%%
% Consult all PL files in a ROS package.
%
cloud_load_user_package(PkgName) :-
	ros_package_path(PkgName,PkgPath),
	atom_concat(PkgPath,'/prolog',PrologDir),
	cloud_load_directory(PrologDir).

%%
% Retract all PL files in a directory.
%
cloud_unload_directory(Directory) :-
	directory_files(Directory, Entries),
	forall(
		(	member(File,Entries),
			atomic_list_concat([Directory, '/', File], FilePath),
			exists_file(FilePath),
			is_prolog_source_file(FilePath)
		),
		cloud_unload_file(FilePath)
	).

%%
% Consult all PL files in a directory.
%
cloud_load_directory(Directory) :-
	directory_files(Directory, Entries),
	forall(
		(	member(File,Entries),
			atomic_list_concat([Directory, '/', File], FilePath),
			exists_file(FilePath),
			is_prolog_source_file(FilePath)
		),
		cloud_consult(FilePath)
	).

%%
% Retract a previously consulted file.
%
cloud_unload_file(File) :-
	write('Un-Consult file '), writeln(File),
	forall(
		cloud_user_term(File,Term),
		cloud_retract_term(Term)
	),
	retractall(cloud_user_term(File,_)).

cloud_retract_term(X :- _) :-
	retractall(user:X), !.
cloud_retract_term(X) :-
	retractall(user:X).

%%
% Load a PL file into KnowRob.
%
cloud_consult(File) :-
	cloud_retract(File),
	write('Consult file '), writeln(File),
	open(File, read, Fd),
	read(Fd, First),
	read_data(File, First, Fd),
	close(Fd).

%%
%
cloud_consult_string(ID, GoalStr) :-
	cloud_retract(ID),
	open_string(GoalStr,Fd),
	read(Fd, First),
	read_data(ID, First, Fd),
	close(Fd).

%%
%
cloud_retract(ID) :-
	forall(
		cloud_user_term(ID,Expanded),
		cloud_retract_term(Expanded)
	),
	retractall(cloud_user_term(ID,_)).

%%
% call assertz for terms in a file
%
read_data(_, end_of_file, _) :- !.
read_data(ID, Term, Fd) :-
	expand_term(Term,Expanded),
	assertz(:(user,Expanded)),
	assertz(cloud_user_term(ID,Expanded)),
	read(Fd, Next),
	read_data(ID, Next, Fd).

