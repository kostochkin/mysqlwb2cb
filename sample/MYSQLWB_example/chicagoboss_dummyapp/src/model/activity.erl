-module(activity, [Id, Name::string(), Content::string(), CourseId, Order::integer()]).
-compile(export_all).
-belongs_to(course).
