import pandas as pd
import numpy as np
from sklearn import decomposition as dc
import matplotlib.pyplot as plt
from math import sqrt
from numpy.linalg import norm
import prettyplotlib as ppl
import matplotlib.patches as patches
import math
import brewer2mpl
from matplotlib.colors import LogNorm


def clusterGram(dataFrame, distance_metric = 'euclidean', linkage_method = 'average',
            outfile = None, clusterRows=True, clusterCols=True, timeSeries=False, doCovar=False,
            figsize=(8,10), row_label_color_fun=lambda x: ppl.almost_black, col_label_color_fun=lambda x: ppl.almost_black,
            link_color_func = lambda x: ppl.almost_black):
    import scipy
    import pylab
    import matplotlib.gridspec as gridspec
    import matplotlib as mpl
    """

    Run hierarchical clustering on data. Creates a heatmap of cluster-ordered data
    heavy-lifting is done by:

    gets distances between rows/columns

    y_events = scipy.spatial.distance.pdist(data, distance_metric)

    calculates the closest rows/columns

    Z_events = scipy.cluster.hierarchy.linkage(y_events, linkage_method)

    genereates dendrogram (tree)

    d_events = scipy.cluster.hierarchy.dendrogram(Z_events, no_labels=True)

    set outfile == "None" to inibit saving an eps file (only show it, don't save it)

    """
    data = np.array(dataFrame)
    colLabels = dataFrame.columns
    rowLabels = dataFrame.index
    nRow, nCol = data.shape

    if clusterRows:
        print "getting row distance matrix"
        y_events = scipy.spatial.distance.pdist(data, distance_metric)
        print "calculating linkages"
        Z_events = scipy.cluster.hierarchy.linkage(y_events, linkage_method, metric=distance_metric)

    if clusterCols:
        print "getting column distance matrix"
        y_samples = scipy.spatial.distance.pdist(np.transpose(data), distance_metric)
        print "calculating linkages"
        Z_samples = scipy.cluster.hierarchy.linkage(y_samples, linkage_method, metric=distance_metric)
    else:
        if doCovar:
            raise ValueError

    fig = pylab.figure(figsize=figsize)

    gs = gridspec.GridSpec(18,10)

    ax1 = pylab.subplot(gs[1:, 0:2]) #row dendrogram

    ax1.set_xticklabels([])
    ax1.set_xticks([])
    ax1.set_frame_on(False)

    reordered = data
    event_order = range(nRow)
    if clusterRows:
        d_events = scipy.cluster.hierarchy.dendrogram(Z_events, orientation='right',
                                                      link_color_func=link_color_func,
                                                      labels=rowLabels)
        event_order = d_events['leaves']
        reordered = data[event_order,:]

    labels = ax1.get_yticklabels()


    ax2 = pylab.subplot(gs[0:1, 2:9]) #column dendrogram

    ax2.set_yticklabels([])
    ax2.set_yticks([])
    ax2.set_frame_on(False)

    sample_order = range(nCol)
    if clusterCols:
        d_samples = scipy.cluster.hierarchy.dendrogram(Z_samples, labels=colLabels, leaf_rotation=90,
                                                       link_color_func=link_color_func)
        sample_order = d_samples['leaves']
        reordered = reordered[:,sample_order]

    axmatrix = pylab.subplot(gs[1:, 2:9])
    bds = np.max(abs(reordered))
    if timeSeries:
        norm = mpl.colors.Normalize(vmin=-bds, vmax=bds)
    else:
        norm = None

    if (np.max(reordered) * np.min(reordered)) > 0:
        cmap = pylab.cm.Reds
    else:
        cmap= pylab.cm.RdBu_r

    im = axmatrix.matshow(reordered, aspect='auto', origin='lower', cmap=cmap, norm=norm)
    axmatrix.set_xticks([])
    axmatrix.set_yticks([])
    axcolor = pylab.subplot(gs[1:6, -1])

    cbTicks = [np.min(data), np.mean(data), np.max(data)]
    cb = pylab.colorbar(im, cax=axcolor, ticks=cbTicks, use_gridspec=True)
    pylab.draw()
    [i.set_color(row_label_color_fun(i.get_text())) for i in ax1.get_yticklabels()]
    [i.set_color(col_label_color_fun(i.get_text())) for i in ax2.get_xticklabels()]


    pylab.tight_layout()

    if outfile is not None:
        fig.savefig(outfile)


    return event_order, sample_order


def plot_pca(df, c_scale=None, x_pc=1, y_pc=2, distance='L1', \
             save_as=None, save_format='png', whiten=True, num_vectors=30, \
             figsize=(10, 10), colors_dict=None, markers_dict=None, \
             title='PCA', show_vectors=True, show_point_labels=True, \
             column_ids_dict=None, index_ids_dict=None, \
             show_vector_labels=True, fig=None, ax=None, \
             marker_size=None, vector_width=None, \
              axis_label_size=None, title_size=None, vector_label_size=None, \
              point_label_size=None):
    """
    Given a pandas dataframe, performs PCA and plots the results in a
    convenient single function.

    @param df: Samples x genes pandas dataframe. Samples on the rows,
    genes in the columns
    @param c_scale: Component scaling of the plot, e.g. for making the
    plotted vectors larger or smaller.
    @param x_pc: Integer, which principal component to use for the x-axis
    (usually 1)
    @param y_pc: Integer, which principal component to use for the y-axis
    (usually 2)
    @param distance:
    @param save_as: String, full name of the plot, including the file extension
    @param save_format: String, usually 'png' or 'pdf'
    @param whiten: Boolean, Whether or not to perform 'whitening'
    normalization on the data, which transforms the data so that it is less
    correlated with itself.
    @param num_vectors: Number of vectors to show on the plot
    @param figsize: Figure size in integers, (width, height)
    @param colors_dict: A dictionary of index (samples) to matplotlib colors
    @param markers_dict: A dictionary of index (samples) to matplotlib markers
    @param title: A string, the title of the plot
    @param show_vectors: Boolean, whether or not to show vectors
    @param show_point_labels: Boolean, whether or not to show the index,
    e.g. the sample name, on the plot
    @param column_ids_dict: A dictionary of column names to another
    value, e.g. if the columns are splicing events with a strange ID,
    this could be a dictionary that matches the ID to a gene name.
    @param index_ids_dict: A dictionary of index names to another
    value, e.g. if the indexes are samples with a strange ID, this could be a
     dictionary that matches the ID to a more readable sample name.
    @param show_vector_labels: Boolean. Can be helpful if the vector labels
    are gene names.
    @return: x, y, marker, distance of each vector in the data.
    """


    row_ids = []
    column_ids = []

    if index_ids_dict is not None:
        for ind in df.index:
            try:
                row_ids.append(index_ids_dict[ind])

            except KeyError:
                row_ids.append(ind)
    
        assert len(row_ids) == len(df.index)

    else:
        row_ids = df.index

    if column_ids_dict is not None:

        for col in df.columns:
            try:
                column_ids.append(column_ids_dict[col])

            except KeyError:
                column_ids.append(col)
        
        assert len(column_ids) == len(df.columns)

    else:
        column_ids = df.columns

    df_array = df.as_matrix()

    # perform pca
    n_components = max(x_pc, y_pc, 2)
    pca = dc.PCA(whiten=whiten, n_components=n_components)
    pca.fit(df_array)
    X = pca.transform(df_array)
    (comp_x, comp_y) = (
        pca.components_[x_pc - 1, :], pca.components_[y_pc - 1, :])

    x_list = X[:, x_pc - 1]
    y_list = X[:, y_pc - 1]

    if not c_scale:
        c_scale = .75 * max([norm(point) for point in zip(x_list, y_list)]) / \
                  max([norm(vector) for vector in zip(comp_x, comp_y)])


    size_scale = sqrt(figsize[0] * figsize[1]) / 1.5
    marker_size = size_scale*5 if not(marker_size) else marker_size
    vector_width = .5 if not vector_width else vector_width
    axis_label_size = size_scale*2 if not axis_label_size else axis_label_size
    title_size = size_scale*3 if not title_size else title_size
    vector_label_size = size_scale if not vector_label_size else vector_label_size
    point_label_size = size_scale if not point_label_size else point_label_size

    # sort features by magnitude/contribution to transformation
    comp_magn = []
    for (x, y, an_id) in zip(comp_x, comp_y, column_ids):

        x = x * c_scale
        y = y * c_scale

        if distance == 'L1':
            comp_magn.append((x, y, an_id, abs(y) + abs(x)))

        elif distance == 'L2':
            comp_magn.append((x, y, an_id, math.sqrt((y ** 2) + (x ** 2))))

    # create figure and plot
    if (fig is None) and (ax is None):
        fig, ax = plt.subplots(figsize=figsize)

    for (x, y, an_id) in zip(x_list, y_list, row_ids):

        if colors_dict:
            try:
                color = colors_dict[an_id]
            except:
                color = 'black'
        else:
            color = 'black'

        if markers_dict:
            try:
                marker = markers_dict[an_id]
            except:
                marker = 'x'

        else:
            marker = 'x'

        if show_point_labels:
            if index_ids_dict:
                try:
                    an_id = index_ids_dict[an_id]
                except:
                    pass

            ax.text(x, y, an_id, color=color, size=point_label_size)

        ppl.scatter(ax, x, y, marker=marker, color=color, s=marker_size, edgecolor='gray')


    vectors = sorted(comp_magn, key=lambda item: item[3], reverse=True)[
              :num_vectors]
    for x, y, marker, distance in vectors:

        if show_vectors:
            ppl.plot(ax, [0, x], [0, y], color=ppl.almost_black, linewidth=vector_width)
            if show_vector_labels:
                 if column_ids_dict:
                     try:
                         marker = column_ids_dict[marker]
                     except:
                         pass

                 ax.text(1.1*x, 1.1*y, marker, color='black', size=vector_label_size)

    var_1 = int(pca.explained_variance_ratio_[x_pc - 1] * 100)
    var_2 = int(pca.explained_variance_ratio_[y_pc - 1] * 100)

    ax.set_xlabel(
        'Principal Component {} (Explains {}% Of Variance)'.format(str(x_pc), \
            str(var_1)), size=axis_label_size)
    ax.set_ylabel(
        'Principal Component {} (Explains {}% Of Variance)'.format(str(y_pc), \
            str(var_2)), size=axis_label_size)
    ax.set_title(title, size=title_size)

    if save_as:
        fig.savefig(save_as, format=save_format)

    fig.show()
    return vectors


def skipped_exon_figure(ax, which_axis='y'):
    """
    Adds two annotations to an axis 'ax':
    1. A skipped exon at 'which_axis'=0, e.g. if which_axis='x', at x=0
    2. An included exon at 'which_axis'=1

    @param ax: A matplotlib.axes instance
    @param which_axis: A string, either 'x' or 'y'
    @return: No return value. Modifies the object 'ax' directly by adding a
    skipped exon at 0 and an included exon at 1.

    Example:
    >>> import prettyplotlib as ppl
    >>> from prettyplotlib import plt
    >>> import numpy as np
    >>> fig, ax = plt.subplots(1)
    >>> psi_scores = np.random.uniform(0, 1, 500)
    >>> ppl.hist(ax, psi_scores)
    >>> skipped_exon_figure(ax, 'x')
    """
    # fig.subplots_adjust(left=subplots_adjust_left)
    xmin, xmax, ymin, ymax = ax.axis()
    delta_x = xmax - xmin
    delta_y = ymax - ymin
    leftmost_x = xmin - (.1 * delta_x) if which_axis == 'y' \
        else xmin - (0.05 * delta_x)
    width = 0.04 * delta_x
    height = 0.025 * delta_y

    bottom_y = -0.01
    top_y = 0.975
    # y = -0.1*delta_y

    adjacent_exon_kwargs = {'fill': True, 'width': width, 'height': height,
                            'clip_on': False, 'facecolor': 'white',
                            'edgecolor': ppl.almost_black}
    skipped_exon_kwargs = {'fill': True, 'width': width, 'height': height,
                           'clip_on': False, 'facecolor': ppl.almost_black,
                           'edgecolor': ppl.almost_black}

    if which_axis == 'y':
        # Spliced-out exon at bottom (psi_ci_halves_max_filtered_drop_na = 0)
        ax.add_patch(patches.Rectangle((leftmost_x + width, bottom_y),
                                       **adjacent_exon_kwargs))
        ax.add_patch(patches.Rectangle((leftmost_x + 2 * width, bottom_y),
                                       **adjacent_exon_kwargs))

        # spliced-in exon at top (psi_ci_halves_max_filtered_drop_na = 1)
        ax.add_patch(patches.Rectangle((leftmost_x, top_y),
                                       **adjacent_exon_kwargs))
        ax.add_patch(patches.Rectangle((leftmost_x + width, top_y),
                                       **skipped_exon_kwargs))
        ax.add_patch(patches.Rectangle((leftmost_x + 2 * width, top_y),
                                       **adjacent_exon_kwargs))

    if which_axis == 'x':
        # Spliced-out exon on left (x=0)
        y = -0.1 * delta_y
        ax.add_patch(
            patches.Rectangle((leftmost_x + width, y),
                              **adjacent_exon_kwargs))
        ax.add_patch(patches.Rectangle((leftmost_x + 2 * width, y),
                                       **adjacent_exon_kwargs))

        # spliced-in exon at right (psi_ci_halves_max_filtered_drop_na = 1)
        right_x = 1.0 * delta_x
        ax.add_patch(
            patches.Rectangle((leftmost_x + right_x, y),
                              **adjacent_exon_kwargs))
        ax.add_patch(patches.Rectangle((leftmost_x + width + right_x, y),
                                       **skipped_exon_kwargs))
        ax.add_patch(patches.Rectangle((leftmost_x + 2 * width + right_x, y),
                                       **adjacent_exon_kwargs))

#
def x_with_ties(series, middle, sep=0.05):
#     middle = 1.0
    """
    For making 'lava lamp' plots. Given a pandas series of y-axis values that
    may have some entries with identical values, return an x-axis vector that
    places equal valued entries 'sep' apart from each other. This is an
    alternative to just making a np.ones() vector for the x-axis.

    @param series: a pandas series of values that you are going to plot
    @param middle: The value these multiple values should be centered on,
    e.g. if they're centered around 1, and there's two items with the same
    value, they'll be at 0.975 and 1.025, as this way they are separated by
    0.05 and are centered around 1.
    @param sep: float value indicating how much of the x-axis to put between
    samples
    @return: @rtype: pandas Series object of x-axis positions.
    """
    middle = float(middle)
    x = pd.Series(index=series.index)
    #seen = set([])
    for y in series.dropna().unique():
        same_score = series[series == y]
        if same_score.shape[0] > 1:
            half = same_score.shape[0] / 2
            x[same_score.index] = np.arange(middle - sep * half,
                                            middle + sep * half + sep,
                                            sep)
        else:
            x[same_score.index] = middle
    return x


def label_side_axis_as_title(ax_right, label):
    ax = plt.subplot2grid((ax_right.numRows, ax_right.numCols), (ax_right.rowNum,0))
    ax.set_xlim((0,1))
    ax.set_ylim((0,1))
    ax.axis('off')
    ax_limits = ax.axis() ;
    ax.text(-1, (ax_limits[3]-ax_limits[2])/2,
            label, fontsize=12,
            horizontalalignment='left', verticalalignment='center')

    handles, labels = ax_right.get_legend_handles_labels()
    ax.legend(handles, labels, loc=2, frameon=False, bbox_to_anchor=(-2.0,1.5))

def add_side_legend(ax, **kwargs):
    ax.legend(bbox_to_anchor=(-.3, 1), loc=2, borderaxespad=0., frameon=False, **kwargs)


def rpkm_and_mapping_stats(rpkm, mapping_stats, img_filename, sort_by_reads=False):
    """
    Creates a plot of all the samples and their mapping stats

    @param rpkm: pandas DataFrame of samples on columns, and rows on genes
    for RPKM
    @param mapping_stats: pandas DataFrame of samples on columns, and mapping
    stats from STAR's *.Log.final.out files created by gscripts
    .output_parsers.rna_star_collector.log_final_out
    @param img_filename: file to save the image created to
    @param sort_by_reads: By default
    """
    colors = brewer2mpl.get_map('Set2', 'qualitative', 7).mpl_colors
    greys = brewer2mpl.get_map('Greys', 'sequential', 9).mpl_colormap

    xticks = np.arange(0, mapping_stats.shape[1])
    print 'xticks', xticks
    if sort_by_reads:
        sorted_col = mapping_stats.columns[mapping_stats.ix['Uniquely mapped ' \
                                                            'reads number', :].values.astype(int).argsort()[::-1]]
    else:
        sorted_col = mapping_stats.columns

#     print sorted_col



    fig = plt.figure(figsize=(30,20))

    # this took a shit ton of time to figure out these parameters... don't change
    # unless you are highly confident.
    ax0 = plt.subplot2grid((18,9), (0,2), colspan=7, rowspan=4)
    ax1 = plt.subplot2grid((18,9), (0,1), colspan=1, rowspan=4)
    ax2 = plt.subplot2grid((18,9), (4,2), colspan=7)
    ax3 = plt.subplot2grid((18,9), (5,2), colspan=7)
    ax4 = plt.subplot2grid((18,9), (6,2), colspan=7)
    ax5 = plt.subplot2grid((18,9), (7,2), colspan=7)
    ax6 = plt.subplot2grid((18,9), (8,2), colspan=7)
    ax7 = plt.subplot2grid((18,9), (9,2), colspan=7)
    ax8 = plt.subplot2grid((18,9), (10,2), colspan=7)
    ax9 = plt.subplot2grid((18,9), (11,2), colspan=7)
    ax10 = plt.subplot2grid((18,9), (12,2), colspan=7)
    ax11 = plt.subplot2grid((18,9), (13,2), colspan=7)
    ax12 = plt.subplot2grid((18,9), (14,2), colspan=7)
    ax13 = plt.subplot2grid((18,9), (15,2), colspan=7)
    ax14 = plt.subplot2grid((18,9), (16,2), colspan=7)
    ax15 = plt.subplot2grid((18,9), (17,2), colspan=7)

    axes = [ax0, ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9, ax10, ax11, ax12,
            ax13, ax14, ax15]

    # --- ax0: samples vs RPKM --- #
    ax0.set_title('Samples, sorted by mapped read count -vs- RPKM, sorted in sample with most reads')
    sample_with_most_reads = sorted_col[0]

    # vmin CANNOT be <=0 because of the log transformation, and then
    # this fucks up fig.savefig()
    vmin = 0.1 #rpkm.min().min()
    vmax = rpkm.max().max()

    # print 'vmin', vmin
    # print 'vmax', vmax

    rpkm.sort_index(by=sample_with_most_reads, inplace=True)
    pcolormesh = ax0.pcolormesh(rpkm.ix[:,sorted_col].values,
                   norm=LogNorm(vmin=vmin, vmax=vmax),
                   cmap=greys)
    # plt.colorbar(pcolormesh)

    # --- ax1: sorted FPKM of sample with most reads --- #

    ax1.set_title('Sorted RPKM of\nSample %s'
                  % sorted_col[0])
    ax1.set_xscale('log')

    ylim =(0, rpkm.shape[0])
    ax1.barh(bottom=range(ylim[0], ylim[1]),
             width=rpkm.ix[:, sample_with_most_reads].values.astype(float), linewidth=0,
             color='grey')
    limits = ax1.axis()
#     ax1.set_xlim(left=limits[1], right=limits[0])
    ax1.set_ylim(0, rpkm.shape[0])
    ppl.remove_chartjunk(ax1, ['top', 'left'], grid='x')

    # --- ax2: Input reads and uniquely mapped reads --- #
    # print "mapping_stats.ix['Uniquely mapped reads number',sorted_col]"
    # print mapping_stats.ix['Uniquely mapped reads number',sorted_col]
    # Plot uniquely mapped reads
    ax2.set_yscale('log')
    print "mapping_stats.ix['Uniquely mapped reads number', sorted_col].values.astype(int)"
    print mapping_stats.ix['Uniquely mapped reads number', sorted_col].values.astype(int)
    ppl.bar(ax2, xticks, height=mapping_stats.ix['Uniquely mapped reads number', ].values.astype(int),
           color=colors[0], label='Uniquely mapped reads')
#     ax2.set_xlim(left=limits[1], right=limits[0])

    # Plot input reads on top
    height = mapping_stats.ix['Number of input reads', sorted_col].values.astype(int) - \
        mapping_stats.ix['Uniquely mapped reads number', sorted_col].values.astype(int)


    ax2.bar(xticks, height,
           color=colors[1], linewidth=0,
           bottom=mapping_stats.ix['Uniquely mapped reads number', sorted_col].values.astype(int),
           label='Unmapped reads')

    ppl.remove_chartjunk(ax2, ['top', 'right'], grid='y')
    add_side_legend(ax2, title='Number of reads, log10')

    # --- ax3: % uniquely mapped -- #
    #label_side_axis_as_title(ax3, '% Uniquely mapped reads')

    uniquely_mapped = mapping_stats.ix['Uniquely mapped reads %',sorted_col].values

    # Multi-mapping percentages
    multi_mapped_multiple_loci = mapping_stats.ix['% of reads mapped to multiple loci',sorted_col].values
    multi_mapped_too_many_loci = mapping_stats.ix['% of reads mapped to too many loci',sorted_col].values
    multi_mapped = multi_mapped_multiple_loci + multi_mapped_too_many_loci

    # unmapping percentages
    un_mapped_mismatches = mapping_stats.ix['% of reads unmapped: too many '
                                            'mismatches',sorted_col].values
    un_mapped_too_short = mapping_stats.ix['% of reads unmapped: too short',sorted_col].values
    un_mapped_other = mapping_stats.ix['% of reads unmapped: other',sorted_col].values
    un_mapped = un_mapped_mismatches + un_mapped_too_short + un_mapped_other

    # Plot % uniquely mapped reads
    ax3.bar(xticks, uniquely_mapped,
           color=colors[0], linewidth=0, label='% Uniquely mapped reads')
    ax3.bar(xticks, multi_mapped, bottom=uniquely_mapped,
           color=colors[1], linewidth=0, label='% Multi-mapped reads')
    ax3.bar(xticks, un_mapped, bottom=uniquely_mapped + multi_mapped,
           color=colors[2], linewidth=0, label='% Unmapped reads')

    ax3.set_ylim((0,100))
    ppl.remove_chartjunk(ax3, ['top', 'right'], grid='y')

    add_side_legend(ax3, title="Read mapping stats")
    #ax3.legend(bbox_to_anchor=(-.1, 1), loc=1, borderaxespad=0., frameon=False)


    # --- ax4: total # splices --- #
    # Plot % uniquely mapped reads
    splices_total = mapping_stats.ix['Number of splices: Total',sorted_col].values.astype(float)

    ax4.bar(xticks, splices_total,
           color=colors[0], edgecolor='white', log=True, label='Number of splices: Total, log10')
    #ax4.legend(bbox_to_anchor=(-.1, 1), loc=1, borderaxespad=0., frameon=False)
    add_side_legend(ax4, title="Splicing")
    #ax4.set_title('Splicing stats')
    ppl.remove_chartjunk(ax4, ['top', 'right'], grid='y')

    # --- ax5: splices: GT/AG --- #
    splices_gtag = mapping_stats.ix['Number of splices: GT/AG',sorted_col].values.astype(int)

    ax5.bar(xticks, 100*splices_gtag/splices_total,
           color=colors[1], edgecolor='white', label='% splices: GT/AG')
    #ax5.legend(bbox_to_anchor=(-.1, 1), loc=1, borderaxespad=0., frameon=False)
    add_side_legend(ax5)
    ppl.remove_chartjunk(ax5, ['top', 'right'], grid='y')

    # --- ax6: splices: GC/AG --- #
    splices_gcag = mapping_stats.ix['Number of splices: GC/AG',sorted_col].values.astype(int)

    ax6.bar(xticks, height=100*splices_gcag/splices_total,
    #        bottom=star_mapping_stats.ix['Number of splices: GC/AG',sorted_col].values.astype(int),
           color=colors[2], edgecolor='white', label='% splices: GC/AG')
    #ax6.legend(bbox_to_anchor=(-.1, 1), loc=1, borderaxespad=0., frameon=False)
    add_side_legend(ax6)
    ax6.locator_params(axis='y', nbins=4)
    ppl.remove_chartjunk(ax6, ['top', 'right'], grid='y')


    # --- ax7: splices: AT/AC --- #
    splices_atac = mapping_stats.ix['Number of splices: AT/AC',sorted_col].values.astype(int)
    ax7.bar(xticks, height=100*splices_atac/splices_total,
    #        bottom=star_mapping_stats.ix['Number of splices: GC/AG',sorted_col].values.astype(int),
           color=colors[3], linewidth=0, label='% splices: AT/AC')
    #ax6.legend(bbox_to_anchor=(-.1, 1), loc=1, borderaxespad=0., frameon=False)
    add_side_legend(ax7)
    ax7.locator_params(axis='y', nbins=4)
    ppl.remove_chartjunk(ax7, ['top', 'right'], grid='y')


    # --- ax8: splices: Non-canonical --- #
    splices_noncanonical = mapping_stats.ix['Number of splices: Non-canonical',sorted_col].values.astype(int)
    ax8.bar(xticks, height=100*splices_noncanonical/splices_total,
    #        bottom=star_mapping_stats.ix['Number of splices: GC/AG',sorted_col].values.astype(int),
           color=colors[4], linewidth=0, label='% splices: Non-canonical')
    #ax6.legend(bbox_to_anchor=(-.1, 1), loc=1, borderaxespad=0., frameon=False)
    add_side_legend(ax8)
    ax8.locator_params(axis='y', nbins=4)
    ppl.remove_chartjunk(ax8, ['top', 'right'], grid='y')


    # --- ax9: mismatch rate --- #
    mismatch_rate = mapping_stats.ix['Mismatch rate per base, %',sorted_col].values
    deletion_rate = mapping_stats.ix['Deletion rate per base',sorted_col].values
    insertion_rate = mapping_stats.ix['Insertion rate per base',sorted_col].values

    ax9.bar(xticks, height=mismatch_rate, bottom=insertion_rate+deletion_rate,
           color=colors[0], linewidth=0, label='Mismatch rate, % per base')
    #ax9.set_ylim((0,1))
    #ax9.set_yscale('log')
    #ax9.set_ylim(0,1)
    add_side_legend(ax9, title="Mismatch and indel rates")
    ppl.remove_chartjunk(ax9, ['top', 'right'], grid='y')
    ax9.locator_params(axis='y', nbins=4)


    # -- ax10: insertion rate --- #
    ax10.bar(xticks, height=insertion_rate,
    #        bottom=star_mapping_stats.ix['Number of splices: GC/AG',sorted_col].values.astype(int),
           color=colors[1], linewidth=0, label='Insertion rate, % per base')
    add_side_legend(ax10)
    ppl.remove_chartjunk(ax10, ['top', 'right'], grid='y')

    # --- ax11: deletion rate --- #
    ax11.bar(xticks, height=deletion_rate,
           color=colors[2], linewidth=0, label='Deletion rate, % per base')
    add_side_legend(ax11)
    ppl.remove_chartjunk(ax11, ['top', 'right'], grid='y')
    ax11.locator_params(axis='y', nbins=4)
    #ax9.set_ylim((0,1))
    #ax10.set_yscale('log')
    #ax10.set_ylim(0,1)

    #ax6.legend(bbox_to_anchor=(-.1, 1), loc=1, borderaxespad=0., frameon=False)


    # --- ax12: deletion average length --- #
    deletion_length = mapping_stats.ix['Deletion average length',sorted_col].values
    insertion_length = mapping_stats.ix['Insertion average length',sorted_col].values

    ax12.bar(xticks, height=insertion_length,
    #        bottom=star_mapping_stats.ix['Number of splices: GC/AG',sorted_col].values.astype(int),
           color=colors[0], linewidth=0, label='Insertion average length, bp')
    add_side_legend(ax12, title='Indel sizes')
    ppl.remove_chartjunk(ax12, ['top', 'right'], grid='y')
    ax12.locator_params(axis='y', nbins=4)
    ax12.set_ylim(0, 2)

    # --- ax13: insertion average length --- #
    ax13.bar(xticks, height=deletion_length,
           color=colors[1],linewidth=0, label='Deletion average length, bp')
    add_side_legend(ax13)
    ppl.remove_chartjunk(ax13, ['top', 'right'], grid='y')
    ax13.locator_params(axis='y', nbins=4)
    ax13.set_ylim(0, 2)


    # --- ax14: multimapping reads --- #
    ax14.bar(xticks, height=100*multi_mapped_multiple_loci/multi_mapped,
           color=colors[0],linewidth=0, label='Multiple loci')
    ax14.bar(xticks, height=100*multi_mapped_too_many_loci/multi_mapped,
             bottom=100*multi_mapped_multiple_loci/multi_mapped,
           color=colors[1],linewidth=0, label='Too many loci')
    add_side_legend(ax14, title='Multi-mapping reads (% of multimapping)')
    ax14.locator_params(axis='y', nbins=4)
    ppl.remove_chartjunk(ax14, ['top', 'right'], grid='y')
    ax14.set_ylim(0,100)


    # --- ax14: unmapped reads --- #
    ax15.bar(xticks, height=100*un_mapped_mismatches/un_mapped,
           color=colors[0],linewidth=0, label='Too many mismatches')
    ax15.bar(xticks, height=100*un_mapped_too_short/un_mapped,
             bottom=100*un_mapped_mismatches/un_mapped,
           color=colors[1],linewidth=0, label='Too short')
    ax15.bar(xticks, height=100*un_mapped_other/un_mapped,
             bottom=100*un_mapped_mismatches/un_mapped+100*un_mapped_too_short/un_mapped,
           color=colors[2],linewidth=0, label='Other')
    add_side_legend(ax15, title='Unmapped reads (% of unmapped)')
    ppl.remove_chartjunk(ax15, ['top', 'right'], grid='y')
    ax15.set_ylim(0,100)

    xticks_labels = np.arange(0.4, mapping_stats.shape[1]+0.4)

    for ax in axes:
        if ax == ax1:
            ppl.remove_chartjunk(ax, ['top', 'left'], ticklabels='y')

            continue
        ax.set_xticks(xticks_labels)
        ax.set_xticklabels([x.replace('_', '\n') for x in sorted_col],
                           ha='center', fontsize=11)
        ax.set_xlim((0,mapping_stats.shape[1]))
        ppl.remove_chartjunk(ax, ['top', 'right'])

    # print_current_time()
    # print 'saving pdf....'
    # fig.savefig('%s.pdf' % img_filename)
    # print_current_time()
    # print 'finished saving pdf.'
    fig.tight_layout()
    fig.savefig('%s.png' % img_filename, dpi=500)


def splicing_diagram(ax, bottom_y, highlight=None, height_multiplier=0.025):
    which_axis = 'y'

    limits = ax.axis()
    delta_x = limits[1] - limits[0]
    delta_y = limits[3] - limits[2]
    leftmost_x = -.3 * delta_x if which_axis == 'y' else -0.05
    width = 0.04 * delta_x
    height = height_multiplier * delta_y

    # bottom_y = -0.01
    top_y = 0.975

    highlight_color = ppl.set1[1]

    exon_kwargs = {'fill': True, 'width': width, 'height': height,
                   'clip_on': False, 'facecolor': 'white', #ppl.almost_black,
                   'edgecolor': ppl.almost_black, 'alpha': 0.5}
    intron_kwargs = {'fill': True, 'height': height * 0.5,
                     'clip_on': False, 'facecolor': highlight_color,
                     #ppl.almost_black,
                     'edgecolor': 'none', 'alpha': 0.5}

    ax.add_patch(patches.Rectangle((leftmost_x, bottom_y),
                                   **exon_kwargs))

    ax.add_patch(patches.Rectangle((leftmost_x + 2 * width, bottom_y),
                                   **exon_kwargs))
    ax.add_patch(patches.Rectangle((leftmost_x + 4 * width, bottom_y),
                                   **exon_kwargs))

    # ad alternative splicing markers
    left_alternative = [(leftmost_x + 1 * width, bottom_y + height),
                        (leftmost_x + 1.5 * width, bottom_y + 1.5 * height),
                        (leftmost_x + 2 * width, bottom_y + height)]
    ax.add_patch(patches.PathPatch(patches.Path(left_alternative),
                                   edgecolor=ppl.almost_black, clip_on=False))

    right_alternative = [(leftmost_x + 3 * width, bottom_y + height),
                         (leftmost_x + 3.5 * width, bottom_y + 1.5 * height),
                         (leftmost_x + 4 * width, bottom_y + height)]
    ax.add_patch(patches.PathPatch(patches.Path(right_alternative),
                                   edgecolor=ppl.almost_black, clip_on=False))

    constitutive = [(leftmost_x + 1 * width, bottom_y),
                    (leftmost_x + 2.5 * width, bottom_y - 1 * height),
                    (leftmost_x + 4 * width, bottom_y)]
    ax.add_patch(patches.PathPatch(patches.Path(constitutive),
                                   edgecolor=ppl.almost_black, clip_on=False))

    first_exon_donor = (leftmost_x + 1 * width, bottom_y + 0.5 * height)
    second_exon_acceptor = (leftmost_x + 2 * width, bottom_y + 0.5 * height)
    second_exon_donor = (leftmost_x + 3 * width, bottom_y + 0.5 * height)
    third_exon_acceptor = (leftmost_x + 4 * width, bottom_y + 0.5 * height)
    splice_site_locs = {'first_exon_donor': first_exon_donor,
                        'second_exon_acceptor': second_exon_acceptor,
                        'second_exon_donor': second_exon_donor,
                        'third_exon_acceptor': third_exon_acceptor}

    alt_exon = {'xy': (leftmost_x + 2 * width, bottom_y),
                'width': width, 'height': height}

    bottom_intron = bottom_y + 0.25 * height
    first_alt_intron = {'xy': (leftmost_x + 1 * width, bottom_intron),
                        'width': width}
    second_alt_intron = {'xy': (leftmost_x + 3 * width, bottom_intron),
                         'width': width}
    constitutive_intron = {'xy': (leftmost_x + 1 * width, bottom_intron),
                           'width': 3 * width}
    first_exon_donor_downstream = {
    'xy': (leftmost_x + 1 * width, bottom_intron),
    'width': 0.5 * width}
    second_exon_acceptor_upstream = {
    'xy': (leftmost_x + 1.5 * width, bottom_intron),
    'width': 0.5 * width}
    second_exon_donor_downstream = {
    'xy': (leftmost_x + 3 * width, bottom_intron),
    'width': 0.5 * width}
    third_exon_acceptor_upstream = {
    'xy': (leftmost_x + 3.5 * width, bottom_intron),
    'width': 0.5 * width}

    intron_locs = {'first_alt_intron': first_alt_intron,
                   'second_alt_intron': second_alt_intron,
                   'constitutive_intron': constitutive_intron,
                   'first_exon_donor_downstream': first_exon_donor_downstream,
                   'second_exon_acceptor_upstream': second_exon_acceptor_upstream,
                   'second_exon_donor_downstream': second_exon_donor_downstream,
                   'third_exon_acceptor_upstream': third_exon_acceptor_upstream}

    if highlight is not None:
        if highlight in splice_site_locs:
            ax.add_patch(patches.Ellipse(splice_site_locs[highlight],
                                         width=0.4 * width, height=2 * height,
                                         facecolor=highlight_color, alpha=0.75,
                                         clip_on=False,
                                         edgecolor=highlight_color))
        elif highlight in intron_locs:
            kwargs = intron_kwargs
            kwargs.update(intron_locs[highlight])
            ax.add_patch(patches.Rectangle(**kwargs))
        elif highlight == 'alt_exon':
            kwargs = intron_kwargs
            kwargs.update(alt_exon)
            ax.add_patch(patches.Rectangle(**kwargs))
        else:
            print highlight, 'is not a valid "highlight" argument'
            
