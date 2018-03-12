my_data=[['slashdot','USA','yes',18,'None'],
        ['google','France','yes',23,'Premium'],
        ['digg','USA','yes',24,'Basic'],
        ['kiwitobes','France','yes',23,'Basic'],
        ['google','UK','no',21,'Premium'],
        ['(direct)','New Zealand','no',12,'None'],
        ['(direct)','UK','no',21,'Basic'],
        ['google','USA','no',24,'Premium'],
        ['slashdot','France','yes',19,'None'],
        ['digg','USA','no',18,'None'],
        ['google','UK','no',18,'None'],
        ['kiwitobes','UK','no',19,'None'],
        ['digg','New Zealand','yes',12,'Basic'],
        ['slashdot','UK','no',21,'None'],
        ['google','UK','yes',18,'Basic'],
        ['kiwitobes','France','yes',19,'Basic']]
#树上每一个节点
class decisionnode:#每个节点包含5个实例变量
    def __init__(self,col=-1,value=None,results=None,tb=None,fb=None):
        self.col=col
        self.value=value
        self.results=results
        self.tb=tb
        self.fb=fb
# col：待检验的变量对应的列索引值
# value：结果为true时当前列匹配的值（如一个节点年龄>60为true，则value为年龄>60）
# tb,fb：true或false时当前节点的子树上的节点（如年龄>60true为高龄，则tb=高龄）

def divideset(rows,column,value):#在某一列上进行拆分
    split_function=None
    if isinstance(value,int) or isinstance(value,float):#数值型
        split_function=lambda row:row[column]>=value
    else:
        split_function=lambda row:row[column]==value
    set1=[row for row in rows if split_function(row)]
    set2=[row for row in rows if not split_function(row)]
    return (set1,set2)
#print(divideset(my_data,0,'google'))#可以看出基于第2列的拆分结果不纯
def uniquecounts(rows):#对各种可能的结果进行计数,其他函数利用此函数计算数据集的纯度
    results={}
    for row in rows:
        r=row[len(row)-1]#结果在最后一列
        if r not in results:
            results[r]=0
        results[r]+=1
    return results
#print(uniquecounts(my_data))

#熵
def entropy(rows):#纯度与熵成反比
    from math import log
    results=uniquecounts(rows)
    #计算熵
    ent=0.0
    for r in results.keys():
        p=float(results[r]/len(rows))
        ent=ent-p*log(p,2)
    return ent
# print(entropy(my_data))
# set1,set2=divideset(my_data,2,'yes')
# print(entropy(set1))

#先求出整个群组的熵，利用每个属性的可能取值对群组进行拆分，并求出两个新群组的熵
#通过计算信息增益确定用哪个属性进行拆分
def buildtree(rows,scoref=entropy):
    if len(rows)==0:
        return decisionnode()
    current_score=scoref(rows)
    #记录最佳拆分条件
    best_gain=0.0
    best_criteria=None
    best_sets=None
    column_count=len(rows[0])-1
    for col in range(0,column_count):#遍历数据集中除最后一列的每一列
        column_values={}
        for row in rows:
            column_values[row[col]]=1
        #根据这一列中的每个值，对数据集进行拆分
        for value in column_values.keys():#针对每一列查找用来拆分的最佳值
            (set1,set2)=divideset(rows,col,value)
            #信息增益
            p=float(len(set1))/len(rows)
            gain=current_score-(p*scoref(set1)+(1-p)*scoref(set2))
            if gain>best_gain and len(set1)>0 and len(set2)>0:
                best_gain=gain
                best_criteria=(col,value)
                best_sets=(set1,set2)
    #创建子分支
    if best_gain>0:
        truebranch=buildtree(best_sets[0])
        falsebranch=buildtree(best_sets[1])
        return decisionnode(col=best_criteria[0],value=best_criteria[1],tb=truebranch,fb=falsebranch)
    else:
        return decisionnode(results=uniquecounts(rows))


tree=buildtree(my_data)

#文本显示决策树
def printtree(tree,indent=''):
    #判断是否为叶节点
    if tree.results!=None:
        print(str(tree.results))
    else:
        #打印判断条件
        print(str(tree.col)+':'+str(tree.value)+'?')
        #打印分支
        print(indent+'T->')
        printtree(tree.tb,indent+' ')
        print(indent+'F->')
        printtree(tree.fb,indent+' ')

#print(printtree(tree))

#图形显示决策树
def getwidth(tree):#一个分支的总宽度等于其所有子分支的宽度之和，若节点没有子分支，宽度为1
    if tree.tb==None and tree.fb==None:
        return 1
    return getwidth(tree.tb)+getwidth(tree.fb)

def getdepth(tree):#一个分支的深度等于其最长子分支的总深度值加1
    if tree.tb==None and tree.fb==None:
        return 0
    return max(getdepth(tree.tb),getdepth(tree.fb))+1

from PIL import Image,ImageDraw
def drawtree(tree,jpeg='tree.jpg'):
    w=getwidth(tree)*100
    h=getdepth(tree)*100+120

    img=Image.new('RGB',(w,h),(255,255,255))
    draw=ImageDraw.Draw(img)

    drawnode(draw,tree,w/2,20)
    img.save(jpeg,'JPEG')

def drawnode(draw,tree,x,y):#画节点，先绘制当前节点，计算子节点位置，再在每个子节点上调用drawnode
    if tree.results==None:
        #每个分支的宽度
        w1=getwidth(tree.tb)*100
        w2=getwidth(tree.fb)*100
        #此节点占据的总空间
        left=x-(w1+w2)/2
        right=x+(w1+w2)/2
        #判断条件字符串
        draw.text((x-20,y-10),str(tree.col)+':'+str(tree.value),(0,0,0))
        #到分支的连线
        draw.line((x,y,left+w1/2,y+100),fill=(255,0,0))
        draw.line((x,y,right-w2/2,y+100),fill=(255,0,0))
        #绘制分支的节点
        drawnode(draw,tree.tb,left+w1/2,y+100)
        drawnode(draw,tree.fb,right-w2/2,y+100)
    else:
        txt=' \n'.join(['%s:%d'%v for v in tree.results.items()])
        draw.text((x-20,y),txt,(0,0,0))

#drawtree(tree,jpeg='treeview.jpg')

#输入新的观测数据，用决策树进行分类
def predict(observation,tree):
    if tree.results!=None:
        return tree.results
    else:
        v=observation[tree.col]
        branch=None
        if isinstance(v,int) or isinstance(v,float):
            if v>=tree.value:
                branch=tree.tb
            else:
                branch=tree.fb
        else:
            if v==tree.value:
                branch=tree.tb
            else:
                branch=tree.fb
    return predict(observation,branch)
#print(predict(['(direct)','USA','yes',5],tree))

#避免过拟合，剪枝---检查相同父节点的一组节点，判断若将其合并，熵的增加是否会小于某个指定阈值，若是则合并

def prune(tree,mingain):#mingain--最小增益值
    #如果不是叶节点，进行剪枝
    if tree.tb.results==None:
        prune(tree.tb,mingain)
    if tree.fb.results==None:
        prune(tree.fb,mingain)
    #如果两个子分支都是叶节点，判断是否需要合并
    if tree.tb.results!=None and tree.fb.results!=None:
        #构造合并后的数据集
        tb,fb=[],[]
        for v,c in tree.tb.results.items():
            tb+=[[v]]*c
        for v,c in tree.fb.results.items():
            fb+=[[v]]*c
        #检查熵
        delta=entropy(tb+fb)-(entropy(tb)+entropy(fb)/2)
        if delta<mingain:
            tree.tb,tree.fb=None,None
            tree.results=uniquecounts(tb+fb)
