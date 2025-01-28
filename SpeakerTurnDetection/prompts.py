
ins = lambda x : f'''给定多句台词，您的任务是基于文本信息判断相邻两句台词是否属于同一角色。

»»»» 任务要求 »»»»
1. 每行给定一句台词，您需要输出 0 或 1，表示该台词和上一句台词是否由同一角色所说。0 表示不同角色，1 表示同一角色。
2. 结合台词的语义、上下文信息来综合做出判断。
3. 输出结果需与输入的行数严格对应，保持原有台词顺序，不得合并或修改台词内容，避免合并台词内容，将原文与结果按格式一起输出。

»»»» 输入格式 »»»»
sentence1
sentence2
sentence3
...

»»»» 输出格式 »»»»
sentence1<None>
sentence2<0/1>
sentence3<0/1>
...

»»»» 开始判断，遵守上述任务要求和格式 »»»»
{x}'''

ins_fewshot = lambda x : f'''
»»»» 任务要求 »»»»
给定多句台词，您的任务是基于文本信息判断相邻两句台词是否属于同一角色。需要满足以下要求：
1. 每行给定一句台词，您需要输出标签0或1，表示该台词和上一句台词是否由同一角色所说。0表示不同角色，1表示同一角色。
2. 结合台词的语义、上下文信息来综合做出判断。
3. 输出结果需与输入的行数严格对应，保持原有台词顺序，不得合并或修改台词内容，避免合并台词内容，将原文与结果按格式一起输出。

»»»» 输入输出示例 »»»»
输入台词：
Didn't think I'd miss your big day, did you?
Didn't you try to kill him?
Greatest thing we can do in life is find the power to forgive.
Ach.
Some night.
It's beautiful.
Where'd you learn those moves?
Oh, I was just following your lead.
Mm.
He's got lines.
Hey. Uh…

输出结果：
Didn’t think I’d miss your big day, did you? <None>
Didn’t you try to kill him? <0>
Greatest thing we can do in life is find the power to forgive. <0>
Ach. <0>
Some night. <1>
It’s beautiful. <0>
Where’d you learn those moves? <0>
Oh, I was just following your lead. <0>
Mm. <0>
He’s got lines. <1>
Hey. Uh… <0>


»»»» 开始判断，遵守上述任务要求和格式 »»»»
输入台词：
{x}

输出结果：'''

ins_ab = lambda x : f'''»»»» 任务要求 »»»»
给定多句台词，您的任务是基于文本信息判断相邻两句台词是否属于同一角色。需要满足以下要求：
1. 每行给定一句台词，您需要为每一行输出一个标签[A]或[B]，表示该台词和上一句台词是否由同一角色所说。不同的标签表示不同角色，相同的标签表示同一角色。
2. 结合台词的语义、上下文信息来综合做出判断。
3. 输出结果需与输入的行数严格对应，保持原有台词顺序，不得合并或修改台词内容，避免合并台词内容，将原文与结果按格式一起输出。

»»»» 输入输出示例 »»»»
输入台词：
Didn't think I'd miss your big day, did you?
Didn't you try to kill him?
Greatest thing we can do in life is find the power to forgive.
Ach.
Some night.
It's beautiful.
Where'd you learn those moves?
Oh, I was just following your lead.
Mm.
He's got lines.
Hey. Uh…
I just want to thank you.
You know, for everything.
I used to dream the undercity could be like this.
But somewhere, I got consumed by all the ways it wasn't.
I gave up on it.
Gave up on you.
I've never seen you give up on anything, Ekko.
You ever wish you could just stay in one moment?
Sometimes taking a leap forward means…
leaving a few things behind.
I promise I'll never forget this.
You better not.

输出结果：
Didn't think I'd miss your big day, did you? <A>
Didn't you try to kill him? <B>
Greatest thing we can do in life is find the power to forgive. <A>
Ach. <B>
Some night. <B>
It's beautiful. <A>
Where'd you learn those moves? <B>
Oh, I was just following your lead. <A>
Mm. <B>
He's got lines. <B>
Hey. Uh… <A>
I just want to thank you. <A>
You know, for everything. <A>
I used to dream the undercity could be like this. <A>
But somewhere, I got consumed by all the ways it wasn't. <A>
I gave up on it. <A>
Gave up on you. <A>
I've never seen you give up on anything, Ekko. <B>
You ever wish you could just stay in one moment? <A>
Sometimes taking a leap forward means… <B>
leaving a few things behind. <B>
I promise I'll never forget this. <A>
You better not. <B>

»»»» 开始判断，遵守上述任务要求和格式 »»»»
输入台词：
{x}
输出结果：'''