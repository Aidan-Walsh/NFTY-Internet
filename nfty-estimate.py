from scapy.all import *

# from util import *
import ruptures as rpt
import sys
import matplotlib.pyplot as plt
import seaborn as sns
from ground_truth import *
import numpy as np
import math

sns.set_style("whitegrid")
# plt.rcParams["figure.figsize"] = (50,30)
# plt.rcParams["axes.labelsize"] = 70
# plt.rcParams["axes.titlesize"] =  80
# plt.rcParams["lines.linewidth"] = 3
# plt.rcParams["xtick.labelsize"] = 65
# plt.rcParams["ytick.labelsize"] = 65
# plt.rcParams["legend.fontsize"] = 50


def moving_average(x, w):
    return np.convolve(x, np.ones(w), "valid") / w


def get_dispersion(filename):
    r_probe = rdpcap(filename)
    last_pkt = r_probe[0]
    r_dispersion = np.array([])
    all_dispersions = []
    # f = open("dispersions1000","w")
    string = ""
    mean_disps = []
    median_disps = []
    for i in range(1, len(r_probe)):
        if "IP" in r_probe[i]:
            if last_pkt:
                dispersion = float(r_probe[i].time - last_pkt.time)
                last_pkt = r_probe[i]
                if dispersion < 1.5:
                    # f.write(str(dispersion*1000000)+"," + str(i) +"\n")
                    # print(dispersion,i)
                    string += str(dispersion) + ","

                    r_dispersion = np.append(
                        r_dispersion, dispersion
                    )  # removing 0's does nothing
                else:
                    # f.write("reset")
                    # print(r_dispersion)
                    string = string.rstrip(",")
                    # print(string)
                    string = ""
                    all_dispersions.append(r_dispersion)
                    # print("stats",np.mean(r_dispersion), np.median(r_dispersion),np.std(r_dispersion))
                    mean_disps.append(np.mean(r_dispersion))
                    median_disps.append(np.median(r_dispersion))

                    # print("reset")

                    r_dispersion = np.array([])
                    last_pkt = r_probe[i]
            else:
                last_pkt = r_probe[i]
            # r_dispersion = np.append(r_dispersion,dispersion)
        # f.close()
        # print("stats",np.mean(r_dispersion), np.median(r_dispersion),np.std(r_dispersion), k)
        #
    all_dispersions.append(r_dispersion)
    # print(all_dispersions)

    return np.array(all_dispersions)


def mean_dispersion_bl(data):
    processing_cap = []
    for i in range(len(data)):
        dispersions = data[i]
        mean_disp = np.mean(dispersions)
        # print(dispersions, median_disp)
        processing_cap.append(1 / mean_disp)
    return processing_cap


def median_dispersion_bl(data):

    processing_cap = []
    for i in range(len(data)):
        dispersions = data[i]
        median_disp = np.median(dispersions)
        # print(dispersions, median_disp)
        processing_cap.append(1 / median_disp)
    return processing_cap


def min_dispersion_bl(data):

    processing_cap = []
    for i in range(len(data)):
        dispersions = data[i]
        # dispersions = np.extract(dispersions > 0, dispersions)
        smoothed_signal = moving_average(dispersions, 150)
        
            
        
        min_disp = np.min(smoothed_signal)
        # print(dispersions, median_disp)
        processing_cap.append(1 / min_disp)
    return processing_cap


def plot_location_disp(disp_per_location, filename):
    x = []
    y = []
    plt.figure()
    ax = plt.axes()
    for loc, disp in disp_per_location.items():
        for d in disp:
            x.append(loc)
            y.append(d)
            # print(loc,d)
    ax.scatter(x, y, marker="o", s=1000)
    plt.ylabel("Mean dispersion (us)")
    plt.xlabel("ith packet in the train at which drop happens")
    plt.title("Average dispersion observed at different drop locations")
    plt.savefig(filename + "_scatter")


# plot the location of drops histogram
def plot_histogram(data, xlabel, ylabel, title, filename, ylims):
    plt.figure()  # (data)
    ax = plt.axes()
    n, bins, patches = ax.hist(data, bins=5, density=True, facecolor="g", alpha=0.75)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    # plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
    # plt.xlim(40, 160)
    plt.ylim(ylims)
    plt.grid(True)
    plt.savefig(filename)


def plot_boxplot(data, label, title, filename, ylimits):
    data = np.array(data)
    plt.figure()  # (data)
    ax = plt.axes()
    bplot1 = ax.boxplot(
        data.T,
        vert=True,  # vertical box alignment
        patch_artist=True,
        boxprops=dict(facecolor="#ADD8E6", color="#ADD8E6"),  # fill with color
        labels=label,
        sym="",
        showmeans=True,
        meanprops={
            "marker": "o",
            "markerfacecolor": "white",
            "markeredgecolor": "black",
            "markersize": "20",
        },
        medianprops={"linewidth": "5"},
        showfliers=True,
    )
    xy_whisker = [item.get_xydata() for item in bplot1["whiskers"]]
    means = [item.get_xydata() for item in bplot1["means"]]
    medians = [item.get_xydata() for item in bplot1["medians"]]
    for v in medians:
        ax.annotate(
            "{:.2f}".format(v[0][1]),
            xy=(v[0][0], v[0][1]),
            fontsize=50,
            ha="center",
            color="#0000FF",
        )
    index = 0
    alternate = 0
    for v in xy_whisker:
        median_percentage = (
            (v[1][1] - medians[index][0][1]) / medians[index][0][1]
        ) * 100
        if alternate:
            xy_pos = (v[1][0], v[1][1])
            alternate = 0
            index += 1
        else:
            xy_pos = (v[1][0], v[1][1])
            alternate = 1
        # ax.annotate("{:.2f}".format(v[0][1]), xy=v[0],fontsize=35) #, xytext=(x_whisker[v][0], y_whisker[v][0]+1), textcoords='offset points', )
        ax.annotate(
            "{:.2f}".format(v[1][1]) + " (" + "{:.2f}".format(median_percentage) + "%)",
            xy=xy_pos,
            fontsize=50,
            ha="center",
        )  # , xytext=(x_whisker[v][1], y_whisker[v][1]+1), textcoords='offset points', fontsize=35)

    plt.ylabel(label)
    plt.title(title)
    plt.ylim(ylimits)
    plt.show()
    # plt.savefig(filename)


def summarize_drop_location(drop_index, file_prefix):
    all_drops = [item for sublist in drop_index for item in sublist]
    all_first_drops = [item[0] for item in drop_index]
    all_second_drops = [item[1] for item in drop_index if len(item) > 1]
    all_last_drops = [item[-2] for item in drop_index]

    # plot_boxplot(all_drops,["drop indices"],"nth dispersion at which drop happens for all 50 runs",file_prefix + "_alldrop-disp-index",[0,2000])
    print("last", *sorted(all_last_drops))
    print("first", *sorted(all_first_drops))
    # plot_boxplot(all_first_drops,["drop indices"],"nth dispersion at which drop happens for all 50 runs",file_prefix + "_firstdrop-disp-index",[0,2000])
    # plot_boxplot(all_second_drops,["drop indices"],"nth dispersion at which drop happens for all 50 runs",file_prefix + "_seconddrop-disp-index",[0,2000])
    # plot_boxplot(all_last_drops,["drop indices"],"nth dispersion at which drop happens for all 50 runs",file_prefix + "_lastdrop-disp-index",[0,2000])

    # plot_histogram(all_drops,"Drop Location Bin","Frequency of drop locations","Histogram of drop locations for all drops",file_prefix + "hist_alldrops",[0,50])
    # plot_histogram(all_first_drops,"Drop Location Bin","Frequency of drop locations","Histogram of drop locations for all drops",file_prefix + "hist_firstdrops",[0,50])
    # plot_histogram(all_second_drops,"Drop Location Bin","Frequency of drop locations","Histogram of drop locations for all drops",file_prefix + "hist_seconddrops",[0,50])


def summarize_drop_dispersion(drops_mean, drops_median, file_prefix):
    all_after_drop_disps = [item for sublist in drops_median for item in sublist[1:]]
    all_before_drop_disps = [sublist[0] for sublist in drops_median]
    all_last_drop_disps = [item[-1] for item in drops_median]

    plot_boxplot(
        all_after_drop_disps,
        ["dispersion value after drops"],
        "Mean dispersion value after drop happens",
        file_prefix + "_all-after-drop-disp",
        [4, 15],
    )
    plot_boxplot(
        all_before_drop_disps,
        ["dispersion value before drops"],
        "Mean dispersion value before drop happens",
        file_prefix + "_all-before-drop-disp",
        [4, 15],
    )
    first_drop_disps = [sublist[1] for sublist in drops_median]
    plot_boxplot(
        first_drop_disps,
        ["dispersion value after first drop"],
        "Mean dispersion value after first drop happens",
        file_prefix + "_first-after-drop-disp",
        [4, 15],
    )
    second_drop_disps = [sublist[2] for sublist in drops_median if len(sublist) > 2]
    plot_boxplot(
        second_drop_disps,
        ["dispersion value after second drop"],
        "Mean dispersion value after second drop happens",
        file_prefix + "_second-after-drop-disp",
        [4, 15],
    )
    plot_boxplot(
        all_last_drop_disps,
        ["dispersion value after last drop"],
        "Mean dispersion value after last drop happens",
        file_prefix + "_last-after-drop-disp",
        [4, 15],
    )


def plot_drop_frequency(drop_index):
    for points in drop_index:
        print(len(points) - 1)


def main(file_prefix, nf, setup):

    signals = get_dispersion(file_prefix)

    # read_signal(file_prefix)
    data_labels = np.full(np.shape(signals)[0], GROUND_TRUTHS[setup][nf])
    print("data labels: ", data_labels)
    (
        no_drops_average,
        no_drops_median,
        drops_mean,
        drops_median,
        shift_indexes,
        per_location_disp,
    ) = detect_all_drops(signals, nf, setup, 100)
    print("Median-all")
    predictions = median_dispersion_bl(signals)
    calculate_MAPE(data_labels, predictions)
    print("Min-all")
    predictions = min_dispersion_bl(signals)
    calculate_MAPE(data_labels, predictions)
    print("Mean-all")
    predictions = mean_dispersion_bl(signals)
    calculate_MAPE(data_labels, predictions)

    # dispersion_indexes = range(0,1000)

    # summarize_drop_location(drop_index, file_prefix)
    # plot_drop_frequency(drop_index)
    # summarize_drop_dispersion(drops_mean, drops_median, file_prefix)
    # plot_location_disp(per_location_disp, file_prefix)


def drop_predict(signal, algo=None, penalty=None):
    # print(signal)
    if not penalty:
        print("change penalty")
        penalty = 7
    algo = "binseg"
    if algo:
        if algo == "binseg":
            algo = rpt.Binseg(model="rbf").fit(signal)
        elif algo == "bottomUp":
            algo = rpt.BottomUp(model="rbf").fit(signal)
        elif algo == "window":
            algo = rpt.Window(model="rbf").fit(signal)
    else:
        # algo = rpt.Pelt(model="rbf").fit(signal)
        algo = rpt.BottomUp(model="rbf").fit(signal)
        # algo = rpt.Dynp(model="rbf").fit(signal)
        # algo = rpt.KernelCPD(kernel="rbf").fit(signal)
        # print("Binary seg", penalty)
        # algo = rpt.Binseg(model="rbf").fit(signal)
        # algo = rpt.Window(model="rbf").fit(signal)

    result = algo.predict(pen=penalty)
    print("result = ", result)
    return result


def read_signal(file_name):
    signals = []
    f = open(file_name, "r")
    for line in f:
        line = line.strip().split(",")
        line = np.array([float(i) for i in line])
        signals.append(line)
    return np.array(signals)


def calculate_MAPE(true_labels, predicted_labels):
    # err = 100*(np.absolute(true_labels-predicted_labels) / true_labels)
    err = 100 * (np.absolute(np.subtract(true_labels, predicted_labels)) / true_labels)
    print(list(err))
    err = np.array([float(i) for i in err])

    # print(np.shape(err),"before")
    # err = np.extract(err < 1000,err)
    # print(np.shape(err),"after")
    mape = np.mean(err)
    mape_median = np.median(err)
    std = np.std(err)
    iqr = np.subtract(*np.percentile(err, [75, 25]))
    print("Mean, Std, Median, IQR", mape, std, mape_median, iqr)
    # for i in err:
    #     print(i)
    return mape, mape_median, std


def find_weight(signal):
    min_std = 100000000
    min_std_val = 0
    min_val = min(signal)
    max_val = max(signal)
    norm_signal = signal - min_val
    norm_signal = signal / max_val
    for i in range(10, len(signal), 10):
        std = np.std(norm_signal[0:i])
        std_err = std / math.sqrt(i)
        if std_err < min_std:
            min_std = std_err
            min_std_val = i
        if std_err <= 0.01:
            print(i)
            return i
            # exit(1)
    print(min_std_val, min_std)
    return min_std_val


def detect_all_drops(signals, nf, setup, budget=None, algo=None):
    dispersion_indexes = range(0, len(signals[0]))
    no_drops_average = []
    no_drops_median = []
    drops_mean = []
    drops_median = []
    drop_index = []
    terminate = 0
    per_location_drop_disp = {}
    if not budget:
        budget = len(dispersion_indexes) - 1
    for signal in signals:
        print(terminate)
        # signal = datapoint[dispersion_indexes[0]:dispersion_indexes[budget]]
        # w=find_weight(signal)
        w = 150
        # signal = moving_average(signal,w)
        result = drop_predict(signal, algo)
        print("drop result", result)
        all_drops_mean = []
        all_drops_median = []
        if len(result) == 1:
            mean_no_drop = 1000000 * np.mean(signal)
            median_no_drop = 1000000 * np.median(signal)
            print(result, mean_no_drop)
            print(result, median_no_drop)
            no_drops_average.append(mean_no_drop)
            no_drops_median.append(median_no_drop)
            # if(terminate != 20 and terminate != 21):
            drops_mean.append(mean_no_drop)
            drops_median.append(median_no_drop)

            drop_index.append(result)
        else:
            before_mean = 1000000 * np.mean(
                signal[dispersion_indexes[0] : dispersion_indexes[0] + result[0]]
            )
            before_median = 1000000 * np.median(
                signal[dispersion_indexes[0] : dispersion_indexes[0] + result[0]]
            )
            all_drops_mean.append(before_mean)
            all_drops_median.append(before_median)

            for i in range(1, len(result)):
                cur_drop_mean = 1000000 * np.mean(
                    signal[
                        dispersion_indexes[0]
                        + result[i - 1] : dispersion_indexes[0]
                        + result[i]
                    ]
                )
                cur_drop_median = 1000000 * np.median(
                    signal[
                        dispersion_indexes[0]
                        + result[i - 1] : dispersion_indexes[0]
                        + result[i]
                    ]
                )
                # if(cur_drop_median >= 7):
                #     print("found one", result, cur_drop_median)
                if cur_drop_mean >= 2:
                    all_drops_mean.append(cur_drop_mean)
                all_drops_median.append(cur_drop_median)
                if result[i - 1] not in per_location_drop_disp:
                    per_location_drop_disp[result[i - 1]] = []
                per_location_drop_disp[result[i - 1]].append(cur_drop_mean)
            drops_mean.append(all_drops_mean)
            drops_median.append(all_drops_median)
            # if(terminate != 20 and terminate != 21):
            drop_index.append(result)
            # if(len(result) > 2):
            #     # fig, (ax,) = rpt.display(signal, signal, result, figsize=(10, 6))
            #     print(all_drops_median)
            # plt.show()
        # if(terminate >= 79 and terminate <= 81):
        # fig, (ax,) = rpt.display(signal, signal, result, figsize=(10, 6))
        # plt.show()
        terminate += 1
        # fig, (ax,) = rpt.display(signal, signal, result, figsize=(10, 6))
        # fig, (ax,) = rpt.display(signal[800:3500], signal[800:3500], [x-800 for x in result[1:]], figsize=(10, 6),computed_chg_pts_linewidth=0.5,computed_chg_pts_color='r',linewidth=0.5)
        print(all_drops_median, all_drops_mean, result)
        # plt.show()
        #

    print("STATISTICS")

    probes_two_drops = [sublist[1] for sublist in drop_index if len(sublist) > 1]
    string = f""" Total probes with no drops = {len(no_drops_median)}
    Total probes with two drops = {len(probes_two_drops)}
    Total probes with one drop = {len(drops_mean) - len(probes_two_drops)}
    """
    print(string)

    predictions = []
    predictions_median = []

    for i in range(len(drops_mean)):
        shifts_train_dispersion = drops_mean[i]
        shifts_median_dispersion = drops_median[i]
        min_step_mean = np.min(shifts_train_dispersion)
        min_step_median = np.min(shifts_median_dispersion)
        train_dispersion_cap = 1000000 / min_step_mean
        print(train_dispersion_cap, min_step_mean)
        predictions.append(train_dispersion_cap)
        median_dispersion_cap = 1000000 / min_step_median
        predictions_median.append(median_dispersion_cap)

    # for i in range(len(drop_index)):
    #     all_train_disps = []
    #     for shift_idx in range(len(drop_index[i])):
    #         # print(i, shift_idx, "shiftcoes")
    #         if(shift_idx == 0):
    #             disp_idx_start = dispersion_indexes[0]
    #         else:
    #             disp_idx_start = dispersion_indexes[0] + drop_index[i][shift_idx-1]

    #         disp_idx_end = dispersion_indexes[0] + drop_index[i][shift_idx]
    #         # print(disp_idx_end,disp_idx_start, length_train)
    #         sum_dispersions = 0
    #         print(np.shape(signals))
    #         # for signal in signals:
    #         #     sum_dispersions = sum(signals[i])

    #         # train_dispersion = sum_dispersions / (disp_idx_end - disp_idx_start)
    #         train_dispersion = np.mean(signal[disp_idx_start:disp_idx_end])
    #         print(train_dispersion, i)
    #         all_train_disps.append(train_dispersion)
    #     all_train_disps = np.array(all_train_disps)
    #     # all_train_disps = np.extract(all_train_disps > 0.000002,all_train_disps)
    #     if(len(all_train_disps)>0):
    #         train_dispersion = min(all_train_disps)
    #     else:
    #         length_train = disp_idx_end - disp_idx_start
    #         train_dispersion = np.mean(signals[i])
    #     train_dispersion_cap = 1/train_dispersion
    #     print(train_dispersion_cap, train_dispersion)
    #     predictions.append(train_dispersion_cap)
    #     dispersion_data = signals[i,disp_idx_start:disp_idx_end+1]
    #     median_disp = np.median(dispersion_data)
    #     predictions_median.append(1/median_disp)

    # predictions = np.extract(np.array(predictions) > 7000,predictions)
    data_labels = np.full(np.shape(signals)[0], GROUND_TRUTHS[setup][nf])
    if len(data_labels) > len(predictions):
        diff = len(data_labels) - len(predictions)
        data_labels = data_labels[:-diff]
    print("mean SCI")
    calculate_MAPE(data_labels, predictions)
    print("median SCI")
    calculate_MAPE(data_labels, predictions_median)
    # return predictions

    return (
        no_drops_average,
        no_drops_median,
        drops_mean,
        drops_median,
        drop_index,
        per_location_drop_disp,
    )


# plot_boxplot([[b[0]*1000000 for b in drops_mean],[b[0]*1000000 for b in drops_median]],["mean","median"],"Dispersion for 50 runs before the drop","before-drop-1000-wisc2-bg1000pps",[10,20])
# plot_boxplot([[b[1]*1000000 for b in drops_mean],[b[1]*1000000 for b in drops_median]],["mean","median"],"Dispersion for 50 runs after the drop","after-drop-1000-wisc2-bg1000pps",[4,10])


# plot_boxplot([no_drops_average, no_drops_median],["mean",",median"],"dispersion values where no drop happens","no-drop-wisc2-1000-with")
# print(np.mean(data[:,idx]))

if __name__ == "__main__":
    file_prefix = sys.argv[1]
    nf = sys.argv[2]
    setup = sys.argv[3]
    main(file_prefix, nf, setup)
