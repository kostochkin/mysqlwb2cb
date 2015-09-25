-module(student, [Id, Firstname::string(), Lastname::string(), AccountId]).
-compile(export_all).
-belongs_to(account).
-has({student_enrolled_in_courses, many}).

courses() ->
	Ids = [X:course_id() || X <- student_enrolled_in_courses()],
	boss_db:find(course, [{id, 'in', Ids}]).
