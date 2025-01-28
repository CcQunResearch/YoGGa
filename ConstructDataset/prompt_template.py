import random

pn_zh2en_source = """萤灯姐姐(Sister Yingdeng,)
姐姐升官大喜(Congrats on your promotion,)
百事顺意(may everything go your way.)
连姿容神气也远胜往日(You even look more radiant than before.)
你我都出自帝君门下(We both hail from Your Majesty's guidance,)
何须行礼(no need for formalities between us.)
碧旖(Biyi,)
姐姐自离宫后(Since you left the palace,)
一早考取仙阶 升任仙倌(you quickly climbed the ranks to become an immortal attendant,)
如今啊(now,)
已是一阁之首(leading a whole pavilion.)
可见这衍虚天宫众多仙侍(It's clear among the many attendants in Yanxu Heavenly Palace,)
帝君对姐姐(Your Majesty has a)
特别的不同啊(special regard for you.)
帝君可在宫中(Is Your Majesty around?)
此布面从装饰到镶嵌(Every aspect of this fabric,)
都是萤灯掌事亲手所制(is personally crafted by Yingdeng.)
混元玉带破损(The Hunyuan Jade Belt was damaged,)
虽为无知仙侍颜淡所为(though by the careless hands of Yandan,)
但妙法阁仍有失察之责(Magical Pavilion still bears responsibility for the oversight.)
萤灯如今不能侍奉在侧(Now that Yingdeng can't serve by your side,)
帝君常议事至天明(You often work till dawn,)
唯愿这安神之物(hopefully, this calming artifact)
能助帝君安眠(can help you find peace in sleep.)
不必了(No need for that.)
那仙侍虽无知鲁莽(Though the immortal attendant is naive and reckless,)
但已经将玉带补好(she's already repaired the jade belt.)
这布面美意过重(This fabric's sentiment is too heavy,)
甚是铺张(It's quite lavish,)
本君消受不起(I can't accept such extravagance.)"""

pn_zh2en_identify = """萤灯（人名） - Yingdeng
帝君（称谓） - Your Majesty
碧旖（人名） - Biyi
衍虚天宫（机构/地名） - Yanxu Heavenly Palace
仙侍（职位） - immortal attendant
混元玉带（物品） - Hunyuan Jade Belt
颜淡（人名） - Yandan
妙法阁（机构） - Magical Pavilion"""

pn_zh2th_source = """这个(ยานี้)
换成款冬花(ต้องเปลี่ยนเป็นควงตงฮวย)
陪你父亲好好说说话(กลับไปคุยกับพ่อของเจ้าดี ๆ)
伯父都能跟你服软(ขนาดลุงยังสามารถอ่อนให้เจ้าได้)
你就不能跟你父亲(แล้วเจ้าไม่สามารถอ่อนให้กับ)
服个软吗(พ่อของเจ้าเลยหรือ)
皇伯父(เสด็จลุง...)
你要听话(เจ้าต้องเชื่อฟังนะ)
是(พ่ะย่ะค่ะ)
长青(ฉางชิง)
奴婢在(พ่ะย่ะค่ะ)
你觉得晏惜委屈吗(เจ้าคิดว่าเยี่ยนซีอัดอั้นตันใจหรือไม่)
世子对凌王殿下(รัฐทายาทคงยากที่จะให้อภัย)
恐怕难以释怀(ท่านอ๋องหลิง)
当年凌王做下了这件事(ตอนนั้นอ๋องหลิงทำเรื่องนี้ลงไป)
朕不戳破(เราไม่เปิดโปง)
他便以为神不知鬼不觉(เขาก็คิดว่าไม่มีผู้ใดรู้เรื่อง)
欠下的账也终归要还的(หนี้ที่ติดค้างไว้ อย่างไรก็ต้องชดใช้)
何况(อีกอย่าง)
晏惜是朕养大的(เราเป็นคนเลี้ยงเยี่ยนซีจนโต)
如今晏惜受了委屈(บัดนี้เยี่ยนซีต้องอัดอั้นตันใจ)
那朕就替他讨个公道(เช่นนั้นเราก็จะทวงความยุติธรรมให้เขา)
这次(ครั้งนี้)
父亲没回玉清山躲着(ท่านพ่อไม่ได้ไปหลบอยู่ที่เขาอวี้ชิง)
司使忠于官家(เสนาบดีจงรักภักดีต่อฝ่าบาท)
七宿卫便该忠于司使(องครักษ์สัตตะดาราก็ควรจงรักภักดีต่อเสนาบดี)
京中之事(เรื่องในเมืองหลวง)
七宿司无所不知(ไม่มีเรื่องใดที่สำนักสัตตะดาราไม่รู้)"""

pn_zh2th_identify = """款冬花（物品） - ควงตงฮวย
皇伯父（称谓） - เสด็จลุง
长青（人名） - ฉางชิง
晏惜（人名） - เยี่ยนซี
凌王（称谓） - อ๋องหลิง
朕（称谓） - เรา
玉清山（地名） - เขาอวี้ชิง
司使（职位） - เสนาบดี
七宿司（机构） - สำนักสัตตะดารา"""

pn_zh2es_source = """这个(Esto)
换成款冬花(hay que cambiarlo por tusílago,)
伯父都能跟你服软(Incluso puedo pedirte disculpas.)
你就不能跟你父亲(¿No puedes disculparte)
服个软吗(con tu padre?)
皇伯父(Tío.)
你要听话(Debes ser obediente.)
是(Sí.)
长青(Changqing.)
奴婢在(Presente.)
你觉得晏惜委屈吗(¿Crees que Yanxi ha sido agraviado?)
世子对凌王殿下(Me temo que a él le resultará difícil)
恐怕难以释怀(perdonar al príncipe Ling.)
当年凌王做下了这件事(En aquel entonces, el príncipe Ling hizo eso.)
朕不戳破(Si no lo expongo,)
他便以为神不知鬼不觉(pensará que nadie se da cuenta.)
欠下的账也终归要还的(Las deudas contraídas deben pagarse.)
何况(Además,)
晏惜是朕养大的(Yanxi fue criado por mí.)
如今晏惜受了委屈(Ahora que Yanxi ha sido agraviado,)
那朕就替他讨个公道(haré justicia para él.)
这次(Esta vez,)
父亲没回玉清山躲着(no volviste a esconderte en la montaña Yuqing.)
司使忠于官家(Yo, el comandante, soy leal a Su Majestad)
七宿卫便该忠于司使(y los guardias del Departamento de Seguridad son leales a mí.)
京中之事(Así que el Departamento de Seguridad)
七宿司无所不知(debería estar al tanto de todos los asuntos de la capital.)"""

pn_zh2es_identify = """款冬花（物品） - tusílago
皇伯父（称谓） - Tío
长青（人名） - Changqing
晏惜（人名） - Yanxi
凌王（称谓） - príncipe Ling
玉清山（地名） - montaña Yuqing
司使（职位） - el comandante
七宿司（机构） - Departamento de Seguridad"""

pn_zh2vi_source = """这个(Cái này)
换成款冬花(đổi thành khoản đông hoa,)
陪你父亲好好说说话(Nói chuyện tử tế với phụ thân của con.)
那件事(Chuyện kia)
就翻过去吧(hãy để nó sang trang đi.)
伯父都能跟你服软(Bá phụ còn có thể nhượng bộ con.)
你就不能跟你父亲(Chẳng lẽ con không thể nhượng bộ)
服个软吗(phụ thân con sao?)
皇伯父(Hoàng bá phụ.)
你要听话(Con phải vâng lời.)
是(Vâng.)
长青(Trường Thanh.)
奴婢在(Có nô tài.)
你觉得晏惜委屈吗(Ngươi cảm thấy Yến Tích có tủi thân không?)
世子对凌王殿下(E là thế tử khó mà buông bỏ được)
恐怕难以释怀(chuyện Lăng vương điện hạ.)
当年凌王做下了这件事(Năm xưa, Lăng vương làm ra chuyện này)
朕不戳破(trẫm không vạch trần.)
他便以为神不知鬼不觉(Thế là đệ ấy tưởng thần không biết quỷ không hay.)
如今晏惜把旧事捅破了(Nay Yến Tích vạch trần chuyện cũ)
也是好事(cũng là cái tốt.)
欠下的账也终归要还的(Nợ nào rồi cũng phải trả thôi.)
何况(Huống chi,)
晏惜是朕养大的(Yến Tích được trẫm nuôi lớn.)
如今晏惜受了委屈(Nay Yến Tích chịu thiệt thòi,)
那朕就替他讨个公道(trẫm sẽ đòi lại công bằng cho nó.)
祖母(Tổ mẫu.)
您这一撒手(Người nhắm mắt xuôi tay,)
我就再也没有人(con chẳng còn ai)
可以依傍了(để dựa dẫm nữa.)
逆子(Nghịch tử.)
这次(Lần này,)
父亲没回玉清山躲着(phụ thân không về núi Ngọc Thanh trốn sao?)"""

pn_zh2vi_identify = """款冬花（物品） - khoản đông hoa
皇伯父（称谓） - Hoàng bá phụ
长青（人名） - Trường Thanh
晏惜（人名） - Yến Tích
凌王（称谓） - Lăng vương
朕（称谓） - trẫm
祖母（称谓） - Tổ mẫu
玉清山（地名） - núi Ngọc Thanh"""

pn_zh2ms_source = """这个(Ini,)
换成款冬花(tukar kepada terssilage farfara,)
陪你父亲好好说说话(Berbual baik-baik dengan ayahanda awak.)
那件事(Biarkan hal itu)
就翻过去吧(berlalu saja.)
伯父都能跟你服软(Pak cik pun boleh bertolak ansur dengan awak,)
你就不能跟你父亲(tak boleh awak bertolak ansur)
服个软吗(dengan ayahanda awak?)
皇伯父(Pak cik.)
你要听话(Awak dengarlah nasihat pak cik.)
是(Ya.)
长青(Changqing.)
奴婢在(Ya.)
你觉得晏惜委屈吗(Awak rasa Yanxi terkilan tak?)
世子对凌王殿下(Takutlah putera susah nak)
恐怕难以释怀(maafkan Raja Ling.)
当年凌王做下了这件事(Tahun itu, Raja Ling lakukan hal ini,)
朕不戳破(beta tak dedahkannya,)
他便以为神不知鬼不觉(maka dia rasa tiada sesiapa yang tahu.)
如今晏惜把旧事捅破了(Bagus juga Yanxi bocorkan hal lama)
也是好事(sekarang.)
欠下的账也终归要还的(Dia tetap perlu bayar balik hutang.)
何况(Lagipun,)
晏惜是朕养大的(beta yang membesarkan Yanxi.)
如今晏惜受了委屈(Sekarang Yanxi rasa terkilan,)
那朕就替他讨个公道(beta akan tegakkan keadilan untuknya.)
祖母(Nenek.)
您这一撒手(Selepas nenek meninggal dunia,)
我就再也没有人(tiada orang yang saya boleh)
可以依傍了(bergantung lagi.)
逆子(Anak tak taat.)
这次(Kali ini,)
父亲没回玉清山躲着(ayahanda tak balik untuk bersembunyi di Gunung Yuqing?)"""

pn_zh2ms_identify = """款冬花（物品） - terssilage farfara
皇伯父（称谓） - pak cik
长青（人名） - Changqing
晏惜（人名） - Yanxi
凌王（称谓） - Raja Ling
朕（称谓） - beta
祖母（称谓） - Nenek
玉清山（地名） - Gunung Yuqing"""

pn_zh2pt_source = """这个(Troque)
换成款冬花(esse por unha-de-asno,)
陪你父亲好好说说话(Vá e fale com seu pai.)
那件事(Acho que podemos)
就翻过去吧(virar a página.)
伯父都能跟你服软(Se eu sou capaz de flexibilizar as coisas com você,)
你就不能跟你父亲(você não poderia)
服个软吗(flexibilizar com ele?)
皇伯父(Tio.)
你要听话(Tem de ser obediente.)
是(Sim.)
长青(Changqing.)
奴婢在(Estou aqui.)
你觉得晏惜委屈吗(Acha que Yanxi foi injustiçado?)
世子对凌王殿下(Acho que Sua Alteza não perdoe)
恐怕难以释怀(Príncipe Ling facilmente.)
当年凌王做下了这件事(Quando Príncipe Ling fez aquilo,)
朕不戳破(se não tivesse sido exposto,)
他便以为神不知鬼不觉(ele pensou que ninguém percebe.)
如今晏惜把旧事捅破了(Agora Yanxi desenterrou o passado,)
也是好事(isso é bom.)
欠下的账也终归要还的(Dívidas devem ser pagas.)
何况(Além disso,)
晏惜是朕养大的(Yanxi foi criado por mim.)
如今晏惜受了委屈(Agora que Yanxi foi injustiçado,)
那朕就替他讨个公道(tenho de fazer justiça por ele.)
祖母(Vovó.)
您这一撒手(Você me deixou,)
我就再也没有人(não terei mais ninguém)
可以依傍了(com quem contar.)
逆子(Rebelde.)
这次(Dessa vez,)
父亲没回玉清山躲着(não se escondeu de novo no Monte Yuqing.)"""

pn_zh2pt_identify = """款冬花（物品） - unha-de-asno
皇伯父（称谓） - Tio
长青（人名） - Changqing
晏惜（人名） - Yanxi
凌王（称谓） - Príncipe Ling
祖母（称谓） - Vovó
玉清山（地名） - Monte Yuqing"""

pn_zh2id_source = """这个(Ini)
换成款冬花(ganti jadi tussilago,)
陪你父亲好好说说话(Temani ayahmu bicara baik-baik.)
那件事(Peristiwa itu)
就翻过去吧(biarkanlah berlalu.)
伯父都能跟你服软(Aku bahkan bisa mengalah padamu,)
你就不能跟你父亲(apakah kau tidak bisa)
服个软吗(mengalah pada ayahmu?)
皇伯父(Paman.)
你要听话(Kau harus patuh.)
是(Baik.)
长青(Changqing.)
奴婢在(Hamba ada di sini.)
你觉得晏惜委屈吗(Apakah kau merasa Yanxi mengalami ketidakadilan?)
世子对凌王殿下(Takutnya Putra Raja Ling sulit)
恐怕难以释怀(untuk memaafkan Raja Ling.)
当年凌王做下了这件事(Waktu itu Raja Ling melakukan hal seperti itu,)
朕不戳破(tetapi aku tidak membocorkannya,)
他便以为神不知鬼不觉(jadi dia pikir tidak ada yang tahu.)
如今晏惜把旧事捅破了(Sekarang Yanxi membocorkan peristiwa lama itu,)
也是好事(ini juga termasuk hal yang baik.)
欠下的账也终归要还的(Utang pada akhirnya harus dibayar.)
何况(Apalagi,)
晏惜是朕养大的(Yanxi dibesarkan olehku.)
如今晏惜受了委屈(Sekarang Yanxi mengalami perlakuan tidak adil,)
那朕就替他讨个公道(jadi aku akan menegakkan keadilan untuk dia.)
祖母(Nenek.)
您这一撒手(Begitu Nenek melepas tangan,)
我就再也没有人(tidak ada orang lagi)
可以依傍了(yang bisa kuandalkan.)
逆子(Anak durhaka.)
这次(Kali ini,)
父亲没回玉清山躲着(Ayah tidak kembali ke Gunung Yuqing untuk bersembunyi?)"""

pn_zh2id_identify = """款冬花（物品） - tussilago
皇伯父（称谓） - Paman
长青（人名） - Changqing
晏惜（人名） - Yanxi
凌王（称谓） - Raja Ling
朕（称谓） - aku
祖母（称谓） - Nenek
玉清山（地名） - Gunung Yuqing"""

pn_en2zh_source = """Who are you?(你是谁)
I am sheldon's cousin leo.(我是谢尔顿的表弟里奥)
Oh,God.(天啊)
Sheldon does not have a cousin leo.(谢尔顿根本没有一个叫里奥的表弟)
Au contraire.(恰恰相反)
I'm 26 years old.(我今年26岁)
I'm originally from... denton, texas,(我的祖籍是 德克萨斯州的登顿市)
But I was a navy brat, so I was(但我是个海军顽童  所以我从小)
Brought up on a variety of military bases around the world.(是在世界各地的军事基地长大的)
As a result, I've often felt like an outsider--(因此  我总感觉跟群体格格不入)
Never really fitting in,(从没真正融入过)
Which is probably the reason for my substance abuse problem.(这也很可能是我滥用毒品的原因)
Excuse me, we just went over this.(打扰一下  我们刚才还练习过一遍)
As the quintessential middle child, your addiction(作为一个典型的中间儿  你的毒瘾)
Is rooted in your unmet need for attention.(根植于你未被满足的对关注度的需求当中)
Oh, sheldon, are we really going to go with pop psychology?(谢尔顿  我们不是真的要用通俗心理学吧)
For your information, this is all based on solid research.(请注意  这些都是以有力的研究为根据的)
Just stick with the character profile I wrote for you.(完全依照我写给你的性格档案就行了)
Sheldon? I'm sorry.(-谢尔顿  -不好意思)
This is toby loobenfeld.(莱纳德  这位是托比·鲁本菲尔德)
He's a research assistant(他是粒子物理实验室的)
In the particle physics lab,(一名研究助理)
But he also minored in theater at mit.(不过他同时在麻省理工辅修戏剧)
It was more of a double major, actually.(事实上  说双学位更准确些)"""

pn_en2zh_identify = """sheldon（人名） - 谢尔顿
leo（人名） - 里奥
denton（地名） - 登顿
texas（地名） - 德克萨斯州
navy brat（称谓） - 海军顽童
military bases（机构） - 军事基地
character profile（物品） - 性格档案
particle physics lab（机构） - 粒子物理实验室
double major（物品） - 双学位"""

pn_ja2zh_source = """男は マグロ漁船で５年 (男孩子们可以 去捕金枪鱼船上工作五年)
女は吉原よしわらで３年も働きゃ 返せんだろ (女孩子去吉原红灯区工作三年 很快就能还清了)
俺をリングに上げてください (请让我上擂台)
龍になるのがハッタリじゃないって 分からせてみせます (我会向您证明我能成为“人中之龙”)
黙れ 一馬！ (住口 一马！)
俺が勝ったら組に入れてください (如果我赢了 请让我加入组织)
カネは働いて返します (我会将功赎罪的)
負けたら どうすんだ？　あ？ (如果你输了呢？那怎么办？)
そんときは… (那…)
好きにしてください 一馬！ (您想怎么处置我都行 一马！)
お前 何言ってんだよ (你在说什么？)
菅 (克己)
あいつに誰か対戦相手 手配できるか？ (你能给他找个对手吗？)
いつ… ですか？ (什么时候？)
そりゃあ お前 今晩に決まってんだろ (当然是今晚)
ありがとうございます！ (谢谢您 先生)
なんで 黙ってたんだよ お前 なんで 一人で決めちまうんだよ！ (你为什么不和我们商量 就擅自决定一切？)
やめてお兄ちゃん (别说了 阿錦！ 我们不是一家人吗？)
お前 家族じゃなかったのかよ！ 錦！ (别说了 阿錦！ 我们不是一家人吗？)
訳 分かんねえよ もう 風間がヤクザとかよ！ (简直瞎搞 你为什么要加入黑道？)
堂島組のカネに手出してよ… (我们偷了堂岛组的钱！ 我们该怎么办？)
俺は試合に勝つから (我一定会打赢的 搞什么…)
勝って堂島の龍になる (我会打赢 然后成为堂岛之龙)
なって どうする？ (然后呢？)
このクソみてえな世界を 変えるんだよ (我要改变这个糟糕的世界)
お前は何も分かってない (你根本什么都不懂)
極道のことも 龍のことも (无论是黑道 还是“人中之龙”)
俺は お前たちを遠ざけたかった (我一直都想让你们…)
こういう… (远离…)
世界から (这个世界)"""

pn_ja2zh_identify = """マグロ漁船（机构） - 捕金枪鱼船
吉原よしわら（地名） - 吉原红灯区
リング（物品） - 擂台
一馬（人名） - 一马
堂島（人名） - 堂岛
極道（称谓） - 黑道
龍（称号） - 人中之龙
風間（人名） - 风间
錦（人名） - 阿锦"""

pn_ko2zh_source = """자네가 이해하고(你就谅解一下)
뭐 아는 게 있으면 얘기 좀 해 주게(若你知道些什么 就告诉我吧)
내 사례는 넉넉히 하겠네(我会好好酬谢你的)
몇 번을 말씀드립니까(你要我说几次？)
전 의원님을 못 뵌 지 몇 달이 넘었습니다(我已经好几个月没见到医员了)
작은 거라도 좋으니 얘기 좀 해 주게(即使小事也好 你就告诉我吧)
너무 중요해서 그러네(因为我们有非常重要的事)
내 관에는 절대로 알리지 않겠네(我绝不会让官衙的人知道)
어제(昨天)
지율헌에서 일하던 서비라는 의녀가 찾아왔었습니다(有位在持律轩工作 名叫舒菲的医女来找过我)
지율헌 사건에 생존자가 있단 말이냐?(持律轩事件有幸存者吗？)
지금 그 의녀는 어디 있는 것이냐(那位医女现在在哪里？)
잘은 모르겠지만(我不太清楚)
아마 언골로 갔을 겁니다(但她可能去冻谷了)
절 찾아와선(她来找我)
언골에서 난다는 생사초라는 풀에 대해 이것저것 물었거든요(针对生长在那里的生死草 问了许多问题)
죽은 사람을 살리는 풀이니 뭐니(听说那种药草能救活死人)
혼이 빠진 게(她整个人失魂落魄的)
보통 사람으로 보이진 않았습니다(看起来不像正常人)
방금 뭐라 하였느냐(你刚才说什么？)
죽은 사람을 살리는 풀?(能救活死人的药草？)
예(是的)
하나 세상천지 그런 풀이 어디 있겠습니까(但天底下怎么可能有那种药草？)
그 언골이라는 곳이 어디냐(那个名叫冻谷的地方在哪里？)
사시사철 얼음이 어는 계곡이라 하여(那个溪谷一年四季都结冰)
언골이라 부르는데(因此称作冻谷)
동래 북쪽 고미산 속에 있다 들었습니다(我听说它位于东莱北方的高弥山里)
저하께선 여기 계십시오 제가 다녀오겠습니다(邸下 请您待在这里 我去就好)
아니다 혼자 있는 게 더 무섭다(不 独自待着更可怕)
이곳은 벌써 한겨울이구나(这里已经是冬天了啊)
저하 제 뒤에 계십시오(邸下 请您站在我身后)
저하(邸下)
저하 위험합니다(邸下 很危险)
지율헌에서 죽은 의녀들과 같은 옷이다(那身衣服和持律轩死去的医女一样)
네가 지율헌 서비라는 의녀냐?(你是持律轩里叫舒菲的医女吗？)"""

pn_ko2zh_identify = """지율헌（机构） - 持律轩
서비（人名） - 舒菲
언골（地名） - 冻谷
생사초（物品） - 生死草
동래（地名） - 东莱
고미산（地名） - 高弥山
저하（称谓） - 邸下"""

pn_en2de_source = """At least you kept your eyes.(Wenigstens hast du deine Augen behalten.)
His loss.(Sein Pech.)
Piss off.(Verpiss dich.)
Well, I would, but we don't have much time.(Das würde ich, aber die Zeit ist knapp.)
Who the fuck are you?(Wer bist du?)
I'm Vilgefortz of Roggeveen.(Ich bin Vilgefortz von Roggeveen.)
Whatever you lack in talent, you make up for in confidence.(Was dir an Talent fehlt, machst du mit Selbstvertrauen wett.)
She doesn't need confidence. Her father owns half of Creyden.(Das braucht sie nicht. Ihrem Vater gehört halb Creyden.)
So he could swap a hundred horses for her spot here.(Er hat 100 Pferde für ihren Platz eingetauscht.)
Your parents paid Aretuza?(Deine Eltern haben Aretusa bezahlt?)
The Chapter decided it needed students from the best families.(Das Kapitel brauchte Schüler aus den besten Familien.)
But you all must have had a conduit moment?(Aber ihr müsst einen Mittler-Moment gehabt haben?)
We shouldn't be mixing herbs. We shouldn't even be here.(Wir sollen keine Kräuter mischen. Wir sollten nicht mal hier sein.)
You know, if they catch us, they really will expel us.(Wenn wir erwischt werden, werfen sie uns raus.)
There are far worse things than expulsion.(Es gibt weitaus Schlimmeres.)
Like what?(Was zum Beispiel?)
What is this place?(Was ist das für ein Ort?)
Aretuza's windmill.(Aretusas Windmühle.)
Enough bridled chaos to keep the curtains hung...(Genug gezügeltes Chaos, um die Vorhänge aufgehängt und die Fackeln)
and the torches lit, but that's not what we're here for.(angezündet zu halten, aber dafür sind wir nicht da.)"""

pn_en2de_identify = """Vilgefortz（人名） - Vilgefortz
Roggeveen（地名） - Roggeveen
Creyden（地名） - Creyden
Aretuza（地名） - Aretusa
The Chapter（机构） - Das Kapitel"""

pn_en2fr_source = """That dreadful play my wife forced me to attend.(Cette farce grotesque que ma femme m'a forcé à regarder.)
I've never forgiven her.(Je ne lui ai jamais pardonné.)
Colonel Fraser recently returned from Scotland,(Le colonel Fraser est récemment revenu d'Écosse)
and brought us some correspondence.(et nous rapporte de la correspondance.)
I had occasion to travel to France,(J'ai dû me rendre en France,)
thought you would be glad to receive word(j'ai pensé vous donner des nouvelles)
of the generous contributions to our cause.(des généreuses contributions à notre cause.)
Remarkable.(Remarquable.)
-You did this of your own accord? -Aye.(- Vous avez agi de votre propre chef ? - Oui.)
Sit with me, Colonel Fraser.(Venez vous asseoir avec moi.)
You're aware that Clinton is preparing to withdraw from Philadelphia?(Vous savez que Clinton s'apprête à se retirer de Philadelphie ?)
I heard an evacuation is already in progress.(J'ai entendu dire qu'une évacuation était déjà en cours.)
I'm impressed with your cunning in securing these documents.(Je suis impressionné par votre ruse pour sécuriser ces documents.)
You took a Loyalist's favor and turned it into a boon for us.(Transformer un service en une telle aubaine.)
And Colonel Morgan has extolled your bravery on the battlefield at Saratoga.(Et le colonel Morgan a vanté votre bravoure à la bataille de Saratoga.)
Will you do me the honor of accepting command of a battalion?(Me ferez-vous l'honneur d'accepter le commandement d'un bataillon ?)
I, uh…(Je…)
I'd be exceedingly honored, sir.(J'en serais extrêmement honoré, monsieur.)
Very well, then.(Très bien.)
You're appointed Brigadier General.(Vous êtes nommé général de brigade.)
Thank you, sir.(Merci, monsieur.)
Although, the Congress will have to approve your appointment.(Cependant, le Congrès devra approuver votre nomination.)"""

pn_en2fr_identify = """Colonel（称谓） - colonel
Fraser（人名） - Fraser
Scotland（地名） - Écosse
France（地名） - France
Clinton（人名） - Clinton
Philadelphia（地名） - Philadelphie
Morgan（人名） - Morgan
Saratoga（地名） - Saratoga
Brigadier General（职位） - général de brigade
Congress（机构） - Congrès"""

proper_noun_slot_dict = {
    "zh2en": ["中文", "英文", pn_zh2en_source, pn_zh2en_identify],
    "zh2th": ["中文", "泰国语", pn_zh2th_source, pn_zh2th_identify],
    "zh2es": ["中文", "西班牙语", pn_zh2es_source, pn_zh2es_identify],
    "zh2vi": ["中文", "越南语", pn_zh2vi_source, pn_zh2vi_identify],
    "zh2ms": ["中文", "马来语", pn_zh2ms_source, pn_zh2ms_identify],
    "zh2pt": ["中文", "葡萄牙语", pn_zh2pt_source, pn_zh2pt_identify],
    "zh2id": ["中文", "印尼语", pn_zh2id_source, pn_zh2id_identify],
    "en2zh": ["英文", "中文", pn_en2zh_source, pn_en2zh_identify],
    "ja2zh": ["日语", "中文", pn_ja2zh_source, pn_ja2zh_identify],
    "ko2zh": ["韩语", "中文", pn_ko2zh_source, pn_ko2zh_identify],
    "en2de": ["英文", "德语", pn_en2de_source, pn_en2de_identify],
    "en2fr": ["英文", "法语", pn_en2fr_source, pn_en2fr_identify],
}

proper_noun_pe_template = """【要求】
在进行翻译时，某些专有名词是指那些独特且专指某一人名、地名、机构、物品或事件等的名称。翻译专有名词时，需要格外注意不同文化和语言环境下的使用习惯，确保专有名词的准确性尤为重要。现在请你帮助我识别出{}影视剧台词中的专有名词，要求如下：
1. 识别剧中出现的需要专门翻译的名词；
2. 标识出识别到的专有名词的类型，类型仅限于人名、称谓、地名、机构、物品、职位这六个；
3. 如果没有识别到专有名词直接输出“无专有名词”即可，对于一些常用词无需作为专有名词。
4. 如果识别到存在专有名词请直接输出识别结果，并根据译文输出相应专有名词的{}翻译，输出格式参考以下样例。

【样例】
原文：
{}

识别到的专有名词：
{}

【任务】
现在按照前面提到的要求，并参考上面提供的样例，从下面的台词中识别出专有名词及其翻译。
原文：
{}

请按照样例的格式识别上面的原文中的专有名词。注意只需要按照格式输出专有名词的识别结果及其译文即可。
"""

# 与上面第二个要求不一样
proper_noun_train_template = """【要求】
在进行翻译时，某些专有名词是指那些独特且专指某一人名、地名、机构、物品或事件等的名称。翻译专有名词时，需要格外注意不同文化和语言环境下的使用习惯，确保专有名词的准确性尤为重要。现在请你帮助我识别出{}影视剧台词中的专有名词，要求如下：
1. 识别剧中出现的需要专门翻译的名词；
2. 标识出识别到的专有名词的类型，类型包括人名、称谓、地名、机构、物品、职位等；
3. 如果没有识别到专有名词直接输出“无专有名词”即可，对于一些常用词无需作为专有名词。
4. 如果识别到存在专有名词请直接输出识别结果，并根据译文输出相应专有名词的{}翻译，输出格式参考以下样例。

【样例】
原文：
{}

识别到的专有名词：
{}

【任务】
现在按照前面提到的要求，并参考上面提供的样例，从下面的台词中识别出专有名词及其翻译。
原文：
{}

请按照样例的格式识别上面的原文中的专有名词。注意只需要按照格式输出专有名词的识别结果及其译文即可。
"""

# proper_noun_slot_dict = {
#     "zh2en": ["英文", pn_zh2en_source, pn_zh2en_identify],
#     "zh2th": ["泰国语", pn_zh2th_source, pn_zh2th_identify],
#     "zh2es": ["西班牙语", pn_zh2es_source, pn_zh2es_identify],
#     "zh2vi": ["越南语", pn_zh2vi_source, pn_zh2vi_identify],
#     "zh2ms": ["马来语", pn_zh2ms_source, pn_zh2ms_identify],
#     "zh2pt": ["葡萄牙语", pn_zh2pt_source, pn_zh2pt_identify],
#     "zh2id": ["印尼语", pn_zh2id_source, pn_zh2id_identify],
#     "en2zh": ["中文", pn_en2zh_source, pn_en2zh_identify],
# }

# proper_noun_pe_template = """【要求】
# 在进行翻译时，某些专有名词是指那些独特且专指某一人名、地名、机构、物品或事件等的名称。翻译专有名词时，需要格外注意不同文化和语言环境下的使用习惯，确保专有名词的准确性尤为重要。现在请你帮助我识别出影视剧台词中的专有名词，要求如下：
# 1. 识别剧中出现的需要专门翻译的名词；
# 2. 标识出识别到的专有名词的类型，类型仅限于人名、称谓、地名、机构、物品、职位这六个；
# 3. 如果没有识别到专有名词直接输出“无专有名词”即可，对于一些常用词无需作为专有名词。
# 4. 如果识别到存在专有名词请直接输出识别结果，并根据译文输出相应专有名词的{}翻译，输出格式参考以下样例。

# 【样例】
# 原文：
# {}

# 识别到的专有名词：
# {}

# 【任务】
# 现在按照前面提到的要求，并参考上面提供的样例，从下面的台词中识别出专有名词及其翻译。
# 原文：
# {}

# 请按照样例的格式识别上面的原文中的专有名词。注意只需要按照格式输出专有名词的识别结果及其译文即可。
# """

# # 与上面第二个要求不一样
# proper_noun_train_template = """【要求】
# 在进行翻译时，某些专有名词是指那些独特且专指某一人名、地名、机构、物品或事件等的名称。翻译专有名词时，需要格外注意不同文化和语言环境下的使用习惯，确保专有名词的准确性尤为重要。现在请你帮助我识别出影视剧台词中的专有名词，要求如下：
# 1. 识别剧中出现的需要专门翻译的名词；
# 2. 标识出识别到的专有名词的类型，类型包括人名、称谓、地名、机构、物品、职位等；
# 3. 如果没有识别到专有名词直接输出“无专有名词”即可，对于一些常用词无需作为专有名词。
# 4. 如果识别到存在专有名词请直接输出识别结果，并根据译文输出相应专有名词的{}翻译，输出格式参考以下样例。

# 【样例】
# 原文：
# {}

# 识别到的专有名词：
# {}

# 【任务】
# 现在按照前面提到的要求，并参考上面提供的样例，从下面的台词中识别出专有名词及其翻译。
# 原文：
# {}

# 请按照样例的格式识别上面的原文中的专有名词。注意只需要按照格式输出专有名词的识别结果及其译文即可。
# """

######################################################################################################################################################################################################

translation_template = """<<1>>
1.<<2>>
2.<<3>>
3.<<4>>
4.<<5>>

专有名词翻译：
{}

<<6>>
原文：
{}

翻译结果：
"""

yingshi_choice = ['影视', '影视剧', '剧目', '电视剧']
yaoqiu_choice = ['以下要求', '如下要求', '下列要求', '下面的要求']
taici_choice = ['台词', '字幕', '对白']
yiwen_choice = ['译文', '翻译']
tongsuyidong_choice = ['通俗易懂', '浅显易懂', '易于理解', '容易理解']
yuyanfengge_choice = ['语言风格', '表达风格']
yizhi_choice = ['一致', '保持一致', '相匹配', '相一致']
xuyao_choice = ['需要', '要', '必须', '应该']
yitong_choice = ['一同', '一并', '一起']
anzhao_choice = ['按照', '遵照', '遵循']

def get_replace_dict():
    taici = random.choice(taici_choice)
    replace_dict = {
        "<<1>>": [
            f"请将多条<src_lang_str>{random.choice(yingshi_choice)}{taici}翻译成<lang_str>，{random.choice(anzhao_choice)}{random.choice(yaoqiu_choice)}：",
            f"请{random.choice(anzhao_choice)}{random.choice(yaoqiu_choice)}来将多条<src_lang_str>{random.choice(yingshi_choice)}{taici}翻译成<lang_str>：",
            f"翻译以下多条<src_lang_str>{random.choice(yingshi_choice)}{taici}为<lang_str>，{random.choice(anzhao_choice)}{random.choice(yaoqiu_choice)}：",
            f"请{random.choice(anzhao_choice)}{random.choice(yaoqiu_choice)}，将下面的多句<src_lang_str>{random.choice(yingshi_choice)}{taici}译成<lang_str>：",
            f"请{random.choice(anzhao_choice)}{random.choice(yaoqiu_choice)}，把一系列<src_lang_str>{random.choice(yingshi_choice)}{taici}翻译成<lang_str>："
        ],
        "<<2>>": [
            f"{random.choice(yiwen_choice)}{random.choice(xuyao_choice)}口语化，{random.choice(tongsuyidong_choice)}，与<src_lang_str>{taici}{random.choice(yuyanfengge_choice)}{random.choice(yizhi_choice)}。",
            f"{random.choice(yiwen_choice)}{random.choice(xuyao_choice)}与<src_lang_str>{taici}{random.choice(yuyanfengge_choice)}{random.choice(yizhi_choice)}，口语化且{random.choice(tongsuyidong_choice)}。",
            f"确保{random.choice(yiwen_choice)}的语言是口语化的、{random.choice(tongsuyidong_choice)}的，并且{random.choice(yuyanfengge_choice)}{random.choice(xuyao_choice)}与<src_lang_str>的{taici}{random.choice(yizhi_choice)}。"
        ],
        "<<3>>": [
            f"翻译的<lang_str>{taici}{random.choice(xuyao_choice)}与<src_lang_str>长度{random.choice(yizhi_choice)}。",
            f"每句{random.choice(yiwen_choice)}的长度{random.choice(xuyao_choice)}与<src_lang_str>{random.choice(yizhi_choice)}",
            f"<lang_str>{random.choice(yiwen_choice)}{random.choice(xuyao_choice)}与<src_lang_str>原文的长度{random.choice(yizhi_choice)}。",
            f"确保译成<lang_str>的{taici}与其<src_lang_str>原{taici}的长度{random.choice(yizhi_choice)}。",
            f"<lang_str>{random.choice(yiwen_choice)}{random.choice(xuyao_choice)}保持与<src_lang_str>原文相同的长度。",
            f"翻译成<lang_str>的{taici}长度{random.choice(xuyao_choice)}和<src_lang_str>版{random.choice(yizhi_choice)}。"
        ],
        "<<4>>": [
            f"专有名词{random.choice(xuyao_choice)}翻译成指定的译文。",
            f"{random.choice(xuyao_choice)}将专有名词译为规定的对应译文。",
            f"{random.choice(xuyao_choice)}确保将专有名词翻译为指明的译文。",
            f"翻译专有名词时，{random.choice(xuyao_choice)}使用指定的译文。",
            f"{random.choice(xuyao_choice)}将专有名词按照指定方式进行翻译。",
            f"专有名词{random.choice(xuyao_choice)}按照所指定的翻译来准确转译。"
        ],
        "<<5>>": [
            f"确保输出与提供的原文行数{random.choice(yizhi_choice)}，不要合并{taici}，{random.choice(yitong_choice)}输出原文与译文。",
            f"请确保输出{random.choice(yiwen_choice)}与所给原文的行数{random.choice(yizhi_choice)}，避免合并{taici}内容，将原文与译文{random.choice(yitong_choice)}输出。",
            f"输出时{random.choice(xuyao_choice)}保证{random.choice(yiwen_choice)}行数与原始文本{random.choice(yizhi_choice)}，避免将{taici}融合，原文和翻译{random.choice(xuyao_choice)}{random.choice(yitong_choice)}输出。",
            f"不要合并{taici}，将原文与{random.choice(yiwen_choice)}{random.choice(yitong_choice)}输出，输出时{random.choice(yiwen_choice)}行数与<src_lang_str>原文{random.choice(yizhi_choice)}。",
            f"将原文与{random.choice(yiwen_choice)}{random.choice(yitong_choice)}输出，注意不能合并{taici}，在输出时{random.choice(yiwen_choice)}行数与<src_lang_str>原文{random.choice(xuyao_choice)}{random.choice(yizhi_choice)}。"
        ],
        "<<6>>": [
            f"现在请{random.choice(anzhao_choice)}要求，完成以下{taici}翻译。",
            f"{random.choice(anzhao_choice)}上面的要求，翻译以下{taici}。",
            f"请{random.choice(anzhao_choice)}前面的要求，翻译下面的{taici}。",
            f"{random.choice(anzhao_choice)}前面所提出的要求，完成下面的{taici}翻译。"
        ]
    }
    return replace_dict