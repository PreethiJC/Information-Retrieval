import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * Created by shikhar.prasoon on 6/10/17.
 */
public class OutputAccuracy {
    private static int totalLowErrorLines = 0;
    private static int totalNormalizedValues = 0;
    public static void main(String[] args) throws IOException {
        String expected = "/Users/Zion/Desktop/NEU/Sem 2/Information Retrieval/HW2/Files/out_stemmed.txt";
        String actual = "//Users/Zion/Desktop/NEU/Sem 2/Information Retrieval/HW2/Files/out.0.stop.stem.txt";
        compareFiles(expected, actual);
    }

    /*
    * takes arguments :
    * 1. file path of expected output
    * 2. file path of actual output (student's version)
     */
    public static void compareFiles(String expected, String actual) throws IOException {
        Map<String, String[]> expected_map = filePath_to_map(expected);
        Map<String, String[]> actual_map = filePath_to_map(actual);

        int errors =
            expected_map
                    .entrySet()
                    .stream()
                    .map(entrySet -> compare(entrySet.getKey(), entrySet.getValue(), actual_map.get(entrySet.getKey())))
                    .filter(bool -> bool)
                    .mapToInt(bool -> {if (bool) return 1; else return 0;})
                    .sum();

        System.out.println("\nFound error in "+errors+" out of "+expected_map.size()+" lines");
        System.out.println("\nErrors < 5% ignored : " + totalLowErrorLines);
        System.out.println("If there is a difference of 1 between 2 values, they are considered equal : for "+totalNormalizedValues+" values");
    }

    private static boolean compare(String term, String[] expectedValues, String[] actualValues) {
        int expectedDF = Integer.parseInt(expectedValues[0]);
        int expectedTTF = Integer.parseInt(expectedValues[1]);
        int actualDF = Integer.parseInt(actualValues[0]);
        int actualTTF = Integer.parseInt(actualValues[1]);

        boolean error = false;
        boolean lowError = false;
        double errorPercentDf = errorPercent(term, expectedDF, actualDF);
        double errorPercentTtf = errorPercent(term, expectedTTF, actualTTF);
        if (errorPercentDf > 5.0) {
            error = true;
            System.out.format("error of %.2f%% in DF for %s. %d instead of %d\n",errorPercentDf,term,expectedDF, actualDF);
        }else if (errorPercentDf > 0.0)
            totalLowErrorLines++;

        if (errorPercentTtf > 5.0) {
            error = true;
            System.out.format("error of %.3f in TTF for %s. %d instead of %d\n", errorPercentTtf, term, expectedTTF, actualTTF);
        }else if (errorPercentTtf > 0.0)
            totalLowErrorLines++;

        return error;
    }

    private static double errorPercent(String term, int expectedValue, int actualValue) {
        int absolute_diff = Math.abs(expectedValue - actualValue);
        if (absolute_diff == 0) {
            return 0.0;
        }
        if (absolute_diff <= 1 && expectedValue>=5) {
            totalNormalizedValues++;
            return 0.0;
        }
//        System.out.println("expected: " + expectedValue);
//        System.out.println("actualValue: " + actualValue);
//        System.out.println("diff: " + (expectedValue - actualValue));
//        System.out.println("%: " + (expectedValue-actualValue)/(double)expectedValue);
        //System.exit(0);
//        System.out.println(tempVar);
        return Math.abs((expectedValue - actualValue) / (double) expectedValue * 100);
    }


    private static Map<String, String[]> filePath_to_map(String filePath) throws IOException {
        return
            Files.lines(Paths.get(filePath))
                    .map(line -> line.split("\\s"))
                    //.map(str_arr -> Arrays.toString(str_arr))
                    //.peek(System.out::println)
                    .collect(Collectors.toMap(
                            str_arr -> str_arr[0],
                            str_arr -> Arrays.copyOfRange(str_arr, 1, str_arr.length)));
            //.entrySet().stream()
            //.forEach(entrySet -> System.out.println(entrySet.getKey() + ": "+ Arrays.toString(entrySet.getValue())))
    }
}
