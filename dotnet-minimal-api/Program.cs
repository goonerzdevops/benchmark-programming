using System.Security.Cryptography;
using System.Text;

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapPost("/complex-transform", (InputData data) =>
{
    var start = DateTime.UtcNow;

    var numericValues = data.Items.Select(x => x.NumericValue).ToList();
    var combinedString = string.Concat(data.Items.Select(x => x.StringData));

    var avgNumeric = numericValues.Count == 0 ? 0 : numericValues.Average();
    var hashed = Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(combinedString))).ToLowerInvariant();

    var transformedItems = data.Items
        .Select(x => new TransformedItem(
            x.NumericValue,
            x.StringData,
            (x.NumericValue * 1.5) + (combinedString.Length / 2.0)
        ))
        .OrderBy(x => x.NewValue)
        .ToList();

    var processingTime = (DateTime.UtcNow - start).TotalMilliseconds;

    return Results.Ok(new
    {
        average_numeric_value = avgNumeric,
        hashed_combined_string = hashed,
        transformed_and_sorted_items = transformedItems,
        server_processing_time_ms = processingTime
    });
});

app.Run();

record Item(double NumericValue, string StringData);
record InputData(List<Item> Items);
record TransformedItem(double OriginalNumeric, string OriginalString, double NewValue);
