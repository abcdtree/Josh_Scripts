library(forcats)
#library(harrietr)
library(ggplot2)
library(ape)
library(ggtree)
library(dplyr)
library(ggnewscale)
library(ggtreeExtra)
library(ggstar)
library(ggtext)
library(treeio)
library(cowplot)


#for(serotype in c("IIIA", "IA", "IB"))
    root_tree <- read.tree("/home/jianszhang/analysis/hav/HAVALL_2022.2/09_23/IB2.tree")
    new_samples <- readLines("/home/jianszhang/analysis/hav/HAVALL_2022.2/09_23/new_IB.txt")

    reroot_phylo_tree <- phytools::midpoint.root(root_tree)
    hav_tree_o <- ggtree(reroot_phylo_tree, layout="rectangular")
    label_list <- get_taxa_name(hav_tree_o)
    new_sample_flag <- c()
    for(label in label_list){
        if(label %in% new_samples){
            new_sample_flag <- append(new_sample_flag, "New")
        }
        else{
            new_sample_flag <- append(new_sample_flag, "History")
        }
    }

    df <- data.frame(label_list, new_sample_flag)
    #print(df)

    hav_tree <- ggtree(reroot_phylo_tree, layout="rectangular")  %<+% df +
    geom_treescale() + geom_tiplab(linesize=.2, aes(color=new_sample_flag),align=TRUE) + geom_tippoint(aes(colour = new_sample_flag, shape = "circle"), size=4) +
    scale_color_manual(values=c(New = "red",History="black"))
    hav_tree_2 <- ggtree(reroot_phylo_tree, layout="rectangular")  %<+% df +
    geom_treescale() + geom_tippoint(aes(colour = new_sample_flag, shape = "circle"), size=4) +
    scale_color_manual(values=c(New = "red",History="black"))
    #ggsave(file="IA.png", plot=hav_tree_2,  width=40, height=40, limitsize=FALSE)

    new_IIIA_nodes <- new_samples
    #for(sample in new_samples){
       # if(grepl("_IIIA", sample, fixed=TRUE)){
        #    new_IIIA_nodes <- append(new_IIIA_nodes, sample)
       # }
    #}

    print(new_IIIA_nodes)
    point_list <- list()
    start <- ""
    end <- ""
    count <- 0
    for(label in rev(label_list)){
        if(count == 0){
            if(label %in% new_IIIA_nodes){
                #count start
                start <- label
                count <- 1
            }else{
                next
            }
        }else if(count == 8){
            if (label %in% new_IIIA_nodes){
                count <-1
            }else{
                #end count
                end <- label
                point_list <- append(point_list, start)
                point_list <- append(point_list, end)
                #print(list(start, end))
                count <- 0
            }
        }else if (label %in% new_IIIA_nodes){
                count <-1
            }else{
                count <- count + 1
            }
    }


    if(count == 1){
        n <- length(label_list)
        point_list <- append(point_list,label_list[n-7])
        point_list <- append(point_list,label_list[n])
    }else if(count == 0){
        #do nothing
        n <- length(label_list)
    }else{
        n <- length(label_list)
        point_list <- append(point_list,start)
        point_list <- append(point_list,label_list[n])
    }

    print(point_list)
    sub_plots <- list()
    for(x in 1:(length(point_list)/2)){
        i <- 2*x -1
        j <- 2*x
        print(MRCA(hav_tree, point_list[i], point_list[j]))
        sub_tree <- viewClade(hav_tree, node=MRCA(hav_tree, point_list[i], point_list[j]))
        sub_plots <- append(sub_plots, sub_tree)
        n <- length(get_taxa_name(sub_tree))*0.1
        ggsave(file=paste0("IB_sub_tree",x,".png", sep="" ), plot=sub_tree,  width=30, height=n, limitsize=FALSE)
    }

    #arrange plot with plot_grid
    #plots <- plot_grid(sub_plots[1], sub_plots[2],labels="AUTO")
    #ggsave(file="subplot.png", plot=plots)
    #sum_plot <- plot_grid(hav_tree_o, plots, nrow=1, align = "l")
    #ggsave(file="combina.png", plot=sum_plot)

    hav_tree_highlight <- hav_tree_2 +
    geom_hilight(node=317, fill="grey") +
    geom_hilight(node=233, fill="grey") 
    #geom_hilight(node=251, fill="grey") 
    #geom_hilight(node=1213, fill="grey") 
    #geom_hilight(node=452, fill="grey") +
    #geom_hilight(node=654, fill="grey")
    #geom_hilight(node=552, fill="grey")
    #geom_hilight(node=551, fill="grey") 

    ggsave(file="IB.png", plot=hav_tree_highlight,  width=30, height=40, limitsize=FALSE)
