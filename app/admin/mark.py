"""作业批改"""
from models.users import User
from . import admin
from servers import homeworks, users
from utils.middleware import login_required
from utils import serialization
from flask import request, make_response
import time
from utils.split import parse_blog
import xlsxwriter
from io import BytesIO
import datetime


# 返回分割点
@admin.route("/homework/<string:task_id>/splits", methods=['GET'])
@login_required("SuperAdmin", "Admin")
def homework_splits(login_user: User, task_id):
    task = homeworks.find_by_id(task_id)
    if not task:
        return serialization.make_resp({"error_msg": "作业不存在"}, code=404)
    return serialization.make_resp({"splits": task.get_splits()}, code=200)


# 获取一个未批改的作业
@admin.route("/homework/<string:task_id>/<string:split_id>", methods=['GET'])
@login_required("SuperAdmin", "Admin")
def homework_split_detail(login_user: User, task_id, split_id):
    task = homeworks.find_by_id(task_id)
    if not task:
        return serialization.make_resp({"error_msg": "作业不存在"}, code=404)
    sp = task.splits.filter_by(id=split_id).first()
    if not sp:
        return serialization.make_resp({"error_msg": "分块不存在"}, code=404)
    doc = sp.get_mongo_doc()
    if not doc:
        return serialization.make_resp({"error_msg": "该作业不存在"}, code=404)
    html = doc["task"]["html"]
    return serialization.make_resp({"split": sp.get_msg(), "html": parse_blog([sp.title], html).get(sp.title, "")}, code=200)


# 提交批改
@admin.route("/homework/<string:task_id>/<string:split_id>", methods=['PUT'])
@login_required("SuperAdmin", "Admin")
def homework_mark(login_user: User, task_id, split_id):
    task = homeworks.find_by_id(task_id)
    if not task:
        return serialization.make_resp({"error_msg": "作业不存在"}, code=404)
    sp = task.splits.filter_by(id=split_id).first()
    if not sp:
        return serialization.make_resp({"error_msg": "分块不存在"}, code=404)
    try:
        scores_json = request.json
        doc_id = scores_json["id"]
        doc = sp.get_mongo_doc_by_id(doc_id)
        if not doc:
            return serialization.make_resp({"error_msg": "作业不存在"}, code=404)
        scores_list = list(scores_json.get("scores"))
    except Exception as e:
        return serialization.make_resp({"error_msg": "参数错误"}, code=400)
    try:
        for score in scores_list:
            s = sp.scores.filter_by(id=score["id"]).first()
            if not s:
                return serialization.make_resp({"error_msg": "评分点不存在"}, code=404)
            if s.max < score["score"] or score["score"] < 0:
                return serialization.make_resp({"error_msg": "分数不在范围内"}, code=400)
            doc["scores"][f'{score["id"]}']["score"] = score["score"]
            doc["scores"][f'{score["id"]}']["referee"] = login_user.name
            doc["scores"][f'{score["id"]}']["mark_at"] = int(time.time())
            sum_score = 0
            for score_doc in doc["scores"].values():
                sum_score += score_doc["score"]
            doc["sum"] = sum_score

    except Exception as e:
        return serialization.make_resp({"error_msg": f"参数错误:{e}"}, code=400)
    doc[f'done_{sp.id}'] = True
    task.get_mongo_group().save(doc)
    return serialization.make_resp({
        "scores": [doc["scores"][f'{score["id"]}'] for score in scores_list]
    }, code=200)


# 上传作业数据
@admin.route("/homework/upload", methods=['POST'])
def upload_task_auto():
    # task = request.json
    task = {
        'data': [{
            'task_id': 4,
            'student_id': '031902321',
            'data': {
                'url': 'https://www.cnblogs.com/danspG/p/14226873.html',
                'html': '<div id="cnblogs_post_body" class="blogpost-body cnblogs-markdown">\n<h1 id="autoid-0-0-0">一、基本情况</h1>\n<h2 id="autoid-1-0-0">1.1 请回望第一次作业，你对于软件工程课程的想象，对比开篇博客你对课程目标和期待，“希望通过实践锻炼，增强计算机专业的能力和就业竞争力”，对比目前的所学所练所得，在哪些方面达到了你的期待和目标，哪些方面还存在哪些不足，为什么？</h2>\n<p><font color="black" size="4">在第一篇博客里我说想要学会一些技能，可以把学过的知识应用起来。<br>\n在整个学期的课程中，我觉得基本达到了我当时的期望。<br>\n学会了使用AS编写app，可以使软件有更好的体验感，其实还是蛮有成就感的；还有在前面作业的一些算法，在解决bug的过程中无论是在百度的、询问同学的，还有在网课中学习的，都让我学到了更多知识，并在解决bug的时候应用起来；还有之前课程学的Java、python，也在作业中有了更好的应用，感觉可以做一些事情。<br>\n其实除了在专业上的，我觉得团队合作也是我很重要的收获，当时就很期待团队合作，到最后，我觉得我们的团队很好，氛围很棒。<br>\n不足的方面，我觉得不管是因为什么原因也好，我觉得一些任务没有做到自己开始对这个任务结果的规划，还是会有一些差别，还是觉得蛮遗憾的。</font></p><font color="black" size="4">\n<h2 id="autoid-1-1-0">1.2 总结这门课程的实践总结和给你带来的提升：</h2>\n<h3 id="autoid-1-2-0">在软工实践课程当中我编写了_____行代码。</h3>\n<h3 id="autoid-1-2-0">软工实践的各次作业分别花费的时间：</h3>\n<div class="table-wrapper"><table>\n<thead>\n<tr>\n<th>#</th>\n<th>作业</th>\n<th>花费时间（分钟）</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td>2</td>\n<td>个人编程作业</td>\n<td>1320</td>\n</tr>\n<tr>\n<td>3</td>\n<td>结对编程作业</td>\n<td>2050</td>\n</tr>\n<tr>\n<td>4</td>\n<td>团队介绍与选题报告</td>\n<td>200</td>\n</tr>\n<tr>\n<td>5</td>\n<td>团队需求分析报告</td>\n<td>240</td>\n</tr>\n<tr>\n<td>6</td>\n<td>团队项目之现场编程</td>\n<td>180</td>\n</tr>\n<tr>\n<td>7-13</td>\n<td>Alpha冲刺（含总结）</td>\n<td>1510</td>\n</tr>\n<tr>\n<td>14-19</td>\n<td>Beta冲刺（含总结）</td>\n<td>1270</td>\n</tr>\n<tr>\n<td>20-22</td>\n<td>每周小结</td>\n<td>150</td>\n</tr>\n</tbody>\n</table></div>\n<h3 id="autoid-1-2-0">讲述令你印象最深刻一次作业？为什么这次作业令你影响深刻？</h3>\n<p>最印象深刻的作业是最后一次团队合作的大作业了。<br>\n因为在这次作业中，我接触了前端，并且可以把app做的比较美观，在自己一步一步编写界面的过程中，真的非常有成绩感，到最后一整个app装在手机上，觉得很欣慰hhhhh；<br>\n当然除了这些，我们的团队也让我非常惊喜，整个团队在过程中共同努力，在一起打代码的过程中，大家更熟悉了，很有团队感，而且我们的组长也是请了两顿饭，很够意思了！</p>\n<h3 id="autoid-1-2-0">在软件工程课程上花费的时间（预计花费时间参考：开篇博客“你打算平均每周拿出多少个小时用在这门课上”的回答）</h3>\n<div class="table-wrapper"><table>\n<thead>\n<tr>\n<th>累计时间</th>\n<th>实际周均时间</th>\n<th>预计周均时间</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td>173</td>\n<td>10.8</td>\n<td>17</td>\n</tr>\n</tbody>\n</table></div>\n<h3 id="autoid-1-2-0">介绍学习到的新技术或生产力工具以及它们给你带来了哪方面的作用？</h3>\n<p>最重要的是AS了，对我来说就是初识前端叭，也加强了以前学过但是忘了不少的Java。</p>\n<h3 id="autoid-1-2-0">其他方面的提升。</h3>\n<p>其他方面其实也有改bug的能力，可能就是百度得更加顺畅了叭hhhh，重点也抓的更好了；<br>\n还有就是团队协作、沟通能力叭，不过大家都各司其职，配合得还不错。</p>\n<h1 id="autoid-1-2-0">二、总结与收获：个人或结对或团队项目实践中的经验总结+实例/例证结合的分析。</h1>\n<p>以团队项目为例（毕竟印象最深刻了），我主要做的是前端，在做的过程中慢慢理解怎么提高用户体验感，还有视觉感受，<br>\n比如在设计按钮的时候，在自己试用过后，之后的调试就会着重考虑按钮的大小、位置这些，虽然比较微笑，但是使用感觉就是不太一样；<br>\n还有刚开始的视频背景，其实只贴图上去也不会有什么过失，但是要是更加贴合主题，更加有美感的话，配置运动视频还是很有吸引力的；<br>\n还有一些跳转之类的，调试过程还是希望尽量符合使用感的，以及感受到前端开发人员真的心很细，还有他们的创意，在自己认识到前段后，在平时使用软件时，也对里面的控件更加敏感。</p>\n<h1 id="autoid-2-0-0">三、这学期下来，你最感谢的人是谁？有什么话想要对TA说呢？</h1>\n</font><p><font color="black" size="4">这学期下来，最感谢的人是一起努力过的团队里的大家了。很感谢他们一起为这个app做的努力，虽然我们的选择比较难，但是大家还是做的很好，大家也可以互相鼓励，共同奋斗，这感觉很好。</font><br>\n<img src="https://img2020.cnblogs.com/blog/2145442/202101/2145442-20210103223124012-1977961901.png" alt="" loading="lazy"></p>\n\n<br><hr><pre>如果您觉得阅读本文对您有帮助，请点一下“<b>推荐</b>”按钮，您的<b>“推荐”</b>将是我最大的写作动力！欢迎各位转载，但是未经作者本人同意，转载文章之后<b>必须在文章页面明显位置给出作者和原文连接</b>，否则保留追究法律责任的权利。</pre></div>',
                'git': 'https://github.com/toolsmen-backend/SoftwareEngineOnline-backend'
            }
        }, {
            'task_id': 4,
            'student_id': '031904103',
            'data': {
                'url': 'https://www.cnblogs.com/danspG/p/14226873.html',
                'html': '<div id="cnblogs_post_body" class="blogpost-body cnblogs-markdown">\n<h1 id="autoid-0-0-0">一、基本情况</h1>\n<h2 id="autoid-1-0-0">1.1 请回望第一次作业，你对于软件工程课程的想象，对比开篇博客你对课程目标和期待，“希望通过实践锻炼，增强计算机专业的能力和就业竞争力”，对比目前的所学所练所得，在哪些方面达到了你的期待和目标，哪些方面还存在哪些不足，为什么？</h2>\n<p><font color="black" size="4">在第一篇博客里我说想要学会一些技能，可以把学过的知识应用起来。<br>\n在整个学期的课程中，我觉得基本达到了我当时的期望。<br>\n学会了使用AS编写app，可以使软件有更好的体验感，其实还是蛮有成就感的；还有在前面作业的一些算法，在解决bug的过程中无论是在百度的、询问同学的，还有在网课中学习的，都让我学到了更多知识，并在解决bug的时候应用起来；还有之前课程学的Java、python，也在作业中有了更好的应用，感觉可以做一些事情。<br>\n其实除了在专业上的，我觉得团队合作也是我很重要的收获，当时就很期待团队合作，到最后，我觉得我们的团队很好，氛围很棒。<br>\n不足的方面，我觉得不管是因为什么原因也好，我觉得一些任务没有做到自己开始对这个任务结果的规划，还是会有一些差别，还是觉得蛮遗憾的。</font></p><font color="black" size="4">\n<h2 id="autoid-1-1-0">1.2 总结这门课程的实践总结和给你带来的提升：</h2>\n<h3 id="autoid-1-2-0">在软工实践课程当中我编写了_____行代码。</h3>\n<h3 id="autoid-1-2-0">软工实践的各次作业分别花费的时间：</h3>\n<div class="table-wrapper"><table>\n<thead>\n<tr>\n<th>#</th>\n<th>作业</th>\n<th>花费时间（分钟）</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td>2</td>\n<td>个人编程作业</td>\n<td>1320</td>\n</tr>\n<tr>\n<td>3</td>\n<td>结对编程作业</td>\n<td>2050</td>\n</tr>\n<tr>\n<td>4</td>\n<td>团队介绍与选题报告</td>\n<td>200</td>\n</tr>\n<tr>\n<td>5</td>\n<td>团队需求分析报告</td>\n<td>240</td>\n</tr>\n<tr>\n<td>6</td>\n<td>团队项目之现场编程</td>\n<td>180</td>\n</tr>\n<tr>\n<td>7-13</td>\n<td>Alpha冲刺（含总结）</td>\n<td>1510</td>\n</tr>\n<tr>\n<td>14-19</td>\n<td>Beta冲刺（含总结）</td>\n<td>1270</td>\n</tr>\n<tr>\n<td>20-22</td>\n<td>每周小结</td>\n<td>150</td>\n</tr>\n</tbody>\n</table></div>\n<h3 id="autoid-1-2-0">讲述令你印象最深刻一次作业？为什么这次作业令你影响深刻？</h3>\n<p>最印象深刻的作业是最后一次团队合作的大作业了。<br>\n因为在这次作业中，我接触了前端，并且可以把app做的比较美观，在自己一步一步编写界面的过程中，真的非常有成绩感，到最后一整个app装在手机上，觉得很欣慰hhhhh；<br>\n当然除了这些，我们的团队也让我非常惊喜，整个团队在过程中共同努力，在一起打代码的过程中，大家更熟悉了，很有团队感，而且我们的组长也是请了两顿饭，很够意思了！</p>\n<h3 id="autoid-1-2-0">在软件工程课程上花费的时间（预计花费时间参考：开篇博客“你打算平均每周拿出多少个小时用在这门课上”的回答）</h3>\n<div class="table-wrapper"><table>\n<thead>\n<tr>\n<th>累计时间</th>\n<th>实际周均时间</th>\n<th>预计周均时间</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td>173</td>\n<td>10.8</td>\n<td>17</td>\n</tr>\n</tbody>\n</table></div>\n<h3 id="autoid-1-2-0">介绍学习到的新技术或生产力工具以及它们给你带来了哪方面的作用？</h3>\n<p>最重要的是AS了，对我来说就是初识前端叭，也加强了以前学过但是忘了不少的Java。</p>\n<h3 id="autoid-1-2-0">其他方面的提升。</h3>\n<p>其他方面其实也有改bug的能力，可能就是百度得更加顺畅了叭hhhh，重点也抓的更好了；<br>\n还有就是团队协作、沟通能力叭，不过大家都各司其职，配合得还不错。</p>\n<h1 id="autoid-1-2-0">二、总结与收获：个人或结对或团队项目实践中的经验总结+实例/例证结合的分析。</h1>\n<p>以团队项目为例（毕竟印象最深刻了），我主要做的是前端，在做的过程中慢慢理解怎么提高用户体验感，还有视觉感受，<br>\n比如在设计按钮的时候，在自己试用过后，之后的调试就会着重考虑按钮的大小、位置这些，虽然比较微笑，但是使用感觉就是不太一样；<br>\n还有刚开始的视频背景，其实只贴图上去也不会有什么过失，但是要是更加贴合主题，更加有美感的话，配置运动视频还是很有吸引力的；<br>\n还有一些跳转之类的，调试过程还是希望尽量符合使用感的，以及感受到前端开发人员真的心很细，还有他们的创意，在自己认识到前段后，在平时使用软件时，也对里面的控件更加敏感。</p>\n<h1 id="autoid-2-0-0">三、这学期下来，你最感谢的人是谁？有什么话想要对TA说呢？</h1>\n</font><p><font color="black" size="4">这学期下来，最感谢的人是一起努力过的团队里的大家了。很感谢他们一起为这个app做的努力，虽然我们的选择比较难，但是大家还是做的很好，大家也可以互相鼓励，共同奋斗，这感觉很好。</font><br>\n<img src="https://img2020.cnblogs.com/blog/2145442/202101/2145442-20210103223124012-1977961901.png" alt="" loading="lazy"></p>\n\n<br><hr><pre>如果您觉得阅读本文对您有帮助，请点一下“<b>推荐</b>”按钮，您的<b>“推荐”</b>将是我最大的写作动力！欢迎各位转载，但是未经作者本人同意，转载文章之后<b>必须在文章页面明显位置给出作者和原文连接</b>，否则保留追究法律责任的权利。</pre></div>',
                'git': 'https://github.com/toolsmen-backend/SoftwareEngineOnline-backend'
            }
        }],
        'len': 20,
        'status': 'OK'
    }
    data_list = list(task["data"])
    for d in data_list:
        task_id, student_id, data = d["task_id"], d["student_id"], d["data"]
        t = homeworks.find_by_id(task_id)
        if not t:
            return serialization.make_resp({"error_msg": "作业不存在"}, code=404)
        user = users.find_by_student_id(student_id)
        if not user:
            return serialization.make_resp({"error_msg": "用户不存在"}, code=404)
        if t.team_type == 0:
            # 个人作业
            task_team = user
        elif t.team_type == 1:
            # 结对作业
            task_team = user.pair
        elif t.team_type == 2:
            # 团队作业
            task_team = user.team
        else:
            return serialization.make_resp({"error_msg": "作业格式错误"}, code=400)
        if not task_team:
            return serialization.make_resp({"error_msg": "查询不到队伍信息"}, code=404)
        t.save_mongo_doc(task_team.id, data)
    return serialization.make_resp({"msg": "提交成功"}, code=200)


# # 导出excel
# @admin.route("/homework/<string:task_id>/excel", methods=['GET'])
# @login_required("SuperAdmin", "Admin")
# def homework_download(login_user: User, task_id):
#     task = homeworks.find_by_id_force(task_id)
#     if not task:
#         return serialization.make_resp({"error_msg": "作业不存在"}, code=404)
#     scores_list = [s["scores"].values() for s in task.get_all_scores()]
#     scores = task.get_scores()
#     print(scores_list)
#     print([score.get_msg() for score in scores])
#     try:
#         out = BytesIO()  # 实例化二进制数据
#         workbook = xlsxwriter.Workbook(out)  # 创建一个Excel实例
#         table = workbook.add_worksheet()
#         for i, score in enumerate(scores):
#             table.write(0, i, f'{score.point}-{score.description}')
#         for row, doc in enumerate(scores_list):
#
#             table.write(row + 1, , )
#         # for row, upload in enumerate(uploads):
#         #     for col, option in enumerate(upload["options"]):
#         #         if types[col] == 1 or types[col] == 4:
#         #             content = option["content"]
#         #         elif types[col] == 2 or types[col] == 3:
#         #             content = ""
#         #             chooses = option["content"].split(";")
#         #             op = wj.options[col].description.split(";")
#         #             for n, c in enumerate(chooses):
#         #                 if c == "1":
#         #                     content += op[n] + ";"
#         #         table.write(row + 1, col, content)
#         workbook.close()
#         filename = f"{task.title}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
#         file = make_response(out.getvalue())
#         out.close()
#         file.headers['Content-Type'] = "application/vnd.ms-excel"
#         file.headers["Cache-Control"] = "no-cache"
#         file.headers['Content-Disposition'] = f"attachment; filename*={filename}"
#         return file
#     except Exception as e:
#         return serialization.make_resp({"error_msg": f"下载失败:e"}, code=500)

