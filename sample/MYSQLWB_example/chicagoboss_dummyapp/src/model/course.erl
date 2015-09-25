-module(course, [Id, Name::string(), Goals::string()]).
-compile(export_all).
-has({student_enrolled_in_courses, many}).
-has({activities, many}).

students() ->
	Ids = [X:student_id() || X <- student_enrolled_in_courses()],
	boss_db:find(student, [{id, 'in', Ids}]).
